from bot import bot, discord
from typing import Optional
import pubchempy as pcp
import requests
import json
import re

metals = ["Li", "Be", "Na", "Mg", "K", "Ca", "Rb", "Sr", "Cs", "Ba", "Fr", "Ra", "Sc", "Y", "Ti", "Zr", "Hf", "V", "Nb", "Ta", "Cr", "Mo", "W", "Mn", "Tc", "Re", "Fe", "Ru", "Os", "Co", "Rh", "Ir", "Ni", "Pd", "Pt", "Cu", "Ag", "Au", "Zn", "Cd", "Hg", "Al", "Ga", "In", "Sn", "Tl", "Pb", "Bi"]

@bot.slash_command(description="Information about a compound/element using the formula or name")
async def cheminfo(interaction: discord.Interaction,
                   formula: Optional[str] = discord.SlashOption(name="formula", description="Formula of the chemical compound", required=False),
                   name: Optional[str] = discord.SlashOption(name="name", description="Name of the chemical compound", required=False)):
    if formula is None and name is None:
        await interaction.send("Please enter a formula or name", ephemeral=True)
        return
    await interaction.response.defer()
    try:
        compound = pcp.get_compounds(name or formula, 'formula' if formula else 'name')[0]
        is_ion = compound.charge != 0
        is_element = not is_ion and len(compound.atoms) == 1
        experimental_properties = await get_experimental_properties(compound.cid)
        atoms = list(map(lambda x: x.element, compound.atoms))
        synonyms = list(filter(lambda x: not re.search(r"[0-9]", x) and x != compound.molecular_formula, compound.synonyms[:10])) or None

        if not is_element and any(x in atoms for x in metals):
            bonding = "Ionic bonds"
        elif any(x in atoms for x in metals):
            bonding = "Metallic bonds (Metal)"
        elif not is_element:
            bonding = "Covalent bonds"
        else:
            bonding = None

        if is_ion:
            bonding = "Can form ionic bonds"

        formula_label = format_formula(compound.molecular_formula)

        embed = discord.Embed(title=f"{synonyms[0] if synonyms else compound.iupac_name} ({formula_label})", color=discord.Color.random())
        embed.description = f"For more information, [click here](https://pubchem.ncbi.nlm.nih.gov/compound/{compound.cid})"
        embed.add_field(name="Molecular Weight", value=f"{round(float(compound.molecular_weight))} g/mol", inline=True)
        if is_element:
            embed.add_field(name="Atomic Number", value=f"{round(compound.atoms[0].number)}", inline=True)

        if experimental_properties["description"]:
            embed.add_field(name=f"Visual description of {'element' if is_element else 'compound'}", value=experimental_properties["description"], inline=False)

        if synonyms:
            embed.add_field(name="Synonyms", value=', '.join(synonyms[:5]), inline=False)

        if experimental_properties["color"]:
            embed.add_field(name="Color", value=experimental_properties["color"], inline=True)

        if bonding:
            embed.add_field(name="Bonding", value=bonding, inline=True)

        if is_ion:
            embed.add_field(name="Charge", value=f"{compound.charge}", inline=True)

        await interaction.send(embed=embed)
    except Exception as e:
        print(e)
        await interaction.send("Invalid formula or name (an error occurred)", ephemeral=True)
    
    
async def get_experimental_properties(cid):
    try:
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON/"
        response = requests.get(url)
        data = json.loads(response.text)
        for section in data["Record"]["Section"]:
            if section["TOCHeading"] == "Chemical and Physical Properties":
                main_section = section
                break
        experimental_properties = None
        for subsection in main_section["Section"]:
            if subsection["TOCHeading"] == "Experimental Properties":
                experimental_properties = subsection
                break

        for property in experimental_properties["Section"]:
            if property["TOCHeading"] == "Physical Description":
                description_of_compound = property["Information"][0]["Value"]["StringWithMarkup"][0]["String"]
                color = property["Information"][1]["Value"]["StringWithMarkup"][0]["String"]
                if color:
                    color = color.split(";")[0]
    
        return {
            "description": description_of_compound,
            "color": color
        }
    except Exception as e:
        print(e)
        return {
            "description": None,
            "color": None
        }

def format_formula(formula: str):
    translations = {
        "+1": "⁺¹",
        "+2": "⁺²",
        "+3": "⁺³",
        "+4": "⁺⁴",
        "+5": "⁺⁵",
        "+6": "⁺⁶",
        "+7": "⁺⁷",
        "-1": "⁻¹",
        "-2": "⁻²",
        "-3": "⁻³",
        "-4": "⁻⁴",
        "-5": "⁻⁵",
        "-6": "⁻⁶",
        "-7": "⁻⁷",
        "0": "₀",
        "1": "₁",
        "2": "₂",
        "3": "₃",
        "4": "₄",
        "5": "₅",
        "6": "₆",
        "7": "₇",
        "8": "₈",
        "9": "₉"
    }
    regex_rule = "|".join(map(re.escape, translations.keys()))
    return re.sub(regex_rule, lambda match: translations[match.group()], formula)
