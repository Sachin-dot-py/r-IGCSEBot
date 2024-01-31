from bot import bot, commands, discord, random, pyshorteners
from data import CIE_IGCSE_SUBJECT_CODES, CIE_OLEVEL_SUBJECT_CODES, CIE_ALEVEL_SUBJECT_CODES, ciealsubjectsdata, cieigsubjectsdata, cieolsubjectsdata

@bot.slash_command(name="random_pyp", description="Gets a random CAIE past year paper.")
async def random_pyp(interaction: discord.Interaction, 
                     programme: str = discord.SlashOption(name="programme", description= "IGCSE, OLEVELS or ALEVELS?", choices=["IGCSE", "O-Level", "A-Level"], required=True),
                     subject_code: str = discord.SlashOption(name="subject_code", description="Enter the subject code", required=True),
                     paper_number: str = discord.SlashOption(name="paper_no", description= "Enter a paper number", required=True)):

            #PAPER_INFORMATION
            INSERT_CODES = ["0410", "0445", "0448", "0449", "0450", "0454", "0457", "0460", "0471", "0500", "0501", "0502", "0503", "0504", "0505", "0508", "0509", "0513", "0514", "0516", "0518", "0538", "9609"]
            YEARS = ["2018", "2019", "2020", "2021", "2022", "2023"]
            PAPER_VARIANT = ["1", "2", "3"]
            SESSIONS = ["s", "w", "m"]
            if programme == "O-Level":
                SESSIONS = ["s", "w"]
              
            PAPER_VARIANT_TWO = ["1", "2"]


            #USAGE OF THE RANDOM VARIABLE
            ranyear = random.choice(YEARS)
            ranvar = random.choice(PAPER_VARIANT)
            ranses = random.choice(SESSIONS)

            #EMPTY_VARIABLES
            sesh = ""

            in_validation = INSERT_CODES.__contains__(subject_code)
            pn_validation = len(paper_number)
            ig_validation = CIE_IGCSE_SUBJECT_CODES.__contains__(subject_code)     
            al_validation = CIE_ALEVEL_SUBJECT_CODES.__contains__(subject_code)
            ol_validation = CIE_OLEVEL_SUBJECT_CODES.__contains__(subject_code)

            if programme == "IGCSE":
                if pn_validation == 1:
                    if paper_number <= "6" and paper_number != "0":
                        if ig_validation:
                            subject_name = cieigsubjectsdata.get(subject_code)
                            if subject_code == "0417" and paper_number in ["2", "3"]:
                                if ranses == "w" and ranyear != ["2019"]:
                                    sesh = "November"
                                    qpv = f"0{paper_number}"
                                    msv = f"{paper_number}"
                                    qpcode = f"{subject_code}_{ranses}{ranyear[2:5]}_qp_{qpv}"
                                    qpurl = pyshorteners.Shortener().tinyurl.short(f"https://edupapers.store/wp-content/uploads/simple-file-list/CIE/{programme}/{subject_name}-{subject_code}/{ranyear}/{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_qp_{qpv}.pdf")
                                    msurl = pyshorteners.Shortener().tinyurl.short(f"https://edupapers.store/wp-content/uploads/simple-file-list/CIE/{programme}/{subject_name}-{subject_code}/{ranyear}/{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_ms_{msv}.pdf")
                                    sfurl = pyshorteners.Shortener().tinyurl.short(f"https://edupapers.store/wp-content/uploads/simple-file-list/CIE/{programme}/{subject_name}-{subject_code}/{ranyear}/{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_sf_{qpv}.zip")
                                    embed = discord.Embed(title=f"Random Paper Chosen", description=f"`{qpcode}` has been chosen at random. Below are links to the question paper, marking scheme and Source Files.\n\n**QP LINK**: {qpurl}\n**MS LINK**: {msurl}\n**SF LINK**: {sfurl}", color=0xf4b6c2)
                                    await interaction.send(embed=embed)
                                elif ranses == "w" and ranyear == "2019":
                                    sesh = "November"
                                    qpv = f"{paper_number}"
                                    msv = f"{paper_number}"
                                    qpcode = f"{subject_code}_{ranses}{ranyear[2:5]}_qp_{qpv}"
                                    qpurl = pyshorteners.Shortener().tinyurl.short(f"https://edupapers.store/wp-content/uploads/simple-file-list/CIE/{programme}/{subject_name}-{subject_code}/{ranyear}/{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_qp_{qpv}.pdf")
                                    msurl = pyshorteners.Shortener().tinyurl.short(f"https://edupapers.store/wp-content/uploads/simple-file-list/CIE/{programme}/{subject_name}-{subject_code}/{ranyear}/{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_ms_{msv}.pdf")
                                    sfurl = pyshorteners.Shortener().tinyurl.short(f"https://edupapers.store/wp-content/uploads/simple-file-list/CIE/{programme}/{subject_name}-{subject_code}/{ranyear}/{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_sf_{qpv}.zip")
                                    embed = discord.Embed(title=f"Random Paper Chosen", description=f"`{qpcode}` has been chosen at random. Below are links to the question paper, marking scheme and Source Files.\n\n**QP LINK**: {qpurl}\n**MS LINK**: {msurl}\n**SF LINK**: {sfurl}", color=0xf4b6c2)
                                    await interaction.send(embed=embed)
                                else:
                                    if ranses == "s":
                                        sesh = "June"
                                        ranvar = random.choice(PAPER_VARIANT_TWO)
                                    else:
                                        sesh = "March"
                                        ranvar = "1"
                                    qpcode = f"{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}"
                                    qpurl = pyshorteners.Shortener().tinyurl.short(f"https://edupapers.store/wp-content/uploads/simple-file-list/CIE/{programme}/{subject_name}-{subject_code}/{ranyear}/{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}.pdf")
                                    msurl = pyshorteners.Shortener().tinyurl.short(f"https://edupapers.store/wp-content/uploads/simple-file-list/CIE/{programme}/{subject_name}-{subject_code}/{ranyear}/{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_ms_{paper_number}{ranvar}.pdf")
                                    sfurl = pyshorteners.Shortener().tinyurl.short(f"https://edupapers.store/wp-content/uploads/simple-file-list/CIE/{programme}/{subject_name}-{subject_code}/{ranyear}/{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_sf_{paper_number}{ranvar}.zip")
                                    embed = discord.Embed(title=f"Random Paper Chosen", description=f"`{qpcode}` has been chosen at random. Below are links to the question paper, marking scheme and Source Files.\n\n**QP LINK**: {qpurl}\n**MS LINK**: {msurl}\n**SF LINK**: {sfurl}", color=0xf4b6c2)
                                    await interaction.send(embed=embed)
                            elif subject_code == "0547":
                                    sesh == "s"
                                    sesh = "June"
                                    qpcode = f"{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}"
                                    qpurl = pyshorteners.Shortener().tinyurl.short(f"https://edupapers.store/wp-content/uploads/simple-file-list/CIE/{programme}/{subject_name}-{subject_code}/{ranyear}/{sesh}/{subject_code}_{sesh}{ranyear[2:5]}_qp_{paper_number}{ranvar}.pdf")
                                    msurl = pyshorteners.Shortener().tinyurl.short(f"https://edupapers.store/wp-content/uploads/simple-file-list/CIE/{programme}/{subject_name}-{subject_code}/{ranyear}/{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_ms_{paper_number}{ranvar}.pdf")
                                    embed = discord.Embed(title=f"Random Paper Chosen", description=f"`{qpcode}` has been chosen at random. Below are links to the question paper, marking scheme and the insert.\n\n**QP LINK**: {qpurl}\n**MS LINK**: {msurl}", color=0xf4b6c2)
                                    await interaction.send(embed=embed)
                            else:
                                if in_validation:
                                    if ranses == "s":
                                        sesh = "June"
                                    elif ranses == "w":
                                         sesh = "November"
                                    else:
                                        sesh = "March"
                                        ranvar = "2"
                                    qpcode = f"{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}"
                                    url = f"https://edupapers.store/wp-content/uploads/simple-file-list/CIE/{programme}/{subject_name}-{subject_code}/{ranyear}/{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}.pdf"
                                    qpurl = pyshorteners.Shortener().tinyurl.short(f"https://edupapers.store/wp-content/uploads/simple-file-list/CIE/{programme}/{subject_name}-{subject_code}/{ranyear}/{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}.pdf")
                                    msurl = pyshorteners.Shortener().tinyurl.short(f"https://edupapers.store/wp-content/uploads/simple-file-list/CIE/{programme}/{subject_name}-{subject_code}/{ranyear}/{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_ms_{paper_number}{ranvar}.pdf")
                                    inurl = pyshorteners.Shortener().tinyurl.short(f"https://edupapers.store/wp-content/uploads/simple-file-list/CIE/{programme}/{subject_name}-{subject_code}/{ranyear}/{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_in_{paper_number}{ranvar}.pdf")
                                    embed = discord.Embed(title=f"Random Paper Chosen", description=f"`{qpcode}` has been chosen at random. Below are links to the question paper, marking scheme and the insert.\n\n**QP LINK**: {qpurl}\n**MS LINK**: {msurl}\n**INSERT LINK**: {inurl}", color=0xf4b6c2)
                                    await interaction.send(embed=embed)
                                else:
                                    if ranses == "s":
                                        sesh = "June"
                                    elif ranses == "w":
                                         sesh = "November"
                                    else:
                                        sesh = "March"
                                        ranvar = "2"
                                    qpcode = f"{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}"
                                    qpurl = pyshorteners.Shortener().tinyurl.short(f"https://edupapers.store/wp-content/uploads/simple-file-list/CIE/{programme}/{subject_name}-{subject_code}/{ranyear}/{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}.pdf")
                                    msurl = pyshorteners.Shortener().tinyurl.short(f"https://edupapers.store/wp-content/uploads/simple-file-list/CIE/{programme}/{subject_name}-{subject_code}/{ranyear}/{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_ms_{paper_number}{ranvar}.pdf")
                                    embed = discord.Embed(title=f"Random Paper Chosen", description=f"`{qpcode}` has been chosen at random. Below are links to the question paper and marking scheme.\n\n**QP LINK**: {qpurl}\n**MS LINK**: {msurl}", color=0xf4b6c2)
                                    await interaction.send(embed=embed)                                        
                        else: await interaction.send("Invalid Subject Code. Please try again.", ephemeral=True)
                    else: await interaction.send("Invalid Paper Number. Please try again.", ephemeral=True)
                else: await interaction.send("Invalid Paper Number. Please try again.", ephemeral=True)

            elif programme == "O-Level":
                if pn_validation == 1:
                    if paper_number <= "6" and paper_number != "0":
                        if ol_validation:
                            subject_name = cieolsubjectsdata.get(subject_code)                 
                            if in_validation:
                                if ranses == "s":
                                    sesh = "June"
                                elif ranses == "w":
                                        sesh = "November"
                                else:
                                    sesh = "March"
                                    ranvar = "2"
                                qpcode = f"{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}"
                                url = f"https://edupapers.store/wp-content/uploads/simple-file-list/CIE/{programme}/{subject_name}-{subject_code}/{ranyear}/{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}.pdf"
                                qpurl = pyshorteners.Shortener().tinyurl.short(f"https://edupapers.store/wp-content/uploads/simple-file-list/CIE/{programme}/{subject_name}-{subject_code}/{ranyear}/{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}.pdf")
                                msurl = pyshorteners.Shortener().tinyurl.short(f"https://edupapers.store/wp-content/uploads/simple-file-list/CIE/{programme}/{subject_name}-{subject_code}/{ranyear}/{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_ms_{paper_number}{ranvar}.pdf")
                                inurl = pyshorteners.Shortener().tinyurl.short(f"https://edupapers.store/wp-content/uploads/simple-file-list/CIE/{programme}/{subject_name}-{subject_code}/{ranyear}/{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_in_{paper_number}{ranvar}.pdf")
                                embed = discord.Embed(title=f"Random Paper Chosen", description=f"`{qpcode}` has been chosen at random. Below are links to the question paper, marking scheme and the insert.\n\n**QP LINK**: {qpurl}\n**MS LINK**: {msurl}\n**INSERT LINK**: {inurl}", color=0xf4b6c2)
                                await interaction.send(embed=embed)
                            else:
                                if ranses == "s":
                                    sesh = "June"
                                elif ranses == "w":
                                        sesh = "November"
                                else:
                                    sesh = "March"
                                    ranvar = "2"
                                qpcode = f"{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}"
                                qpurl = pyshorteners.Shortener().tinyurl.short(f"https://edupapers.store/wp-content/uploads/simple-file-list/CIE/{programme}/{subject_name}-{subject_code}/{ranyear}/{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}.pdf")
                                msurl = pyshorteners.Shortener().tinyurl.short(f"https://edupapers.store/wp-content/uploads/simple-file-list/CIE/{programme}/{subject_name}-{subject_code}/{ranyear}/{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_ms_{paper_number}{ranvar}.pdf")
                                embed = discord.Embed(title=f"Random Paper Chosen", description=f"`{qpcode}` has been chosen at random. Below are links to the question paper and marking scheme.\n\n**QP LINK**: {qpurl}\n**MS LINK**: {msurl}", color=0xf4b6c2)
                                await interaction.send(embed=embed)            
                        else: await interaction.send("Invalid Subject Code. Please try again.", ephemeral=True)
                    else: await interaction.send("Invalid Paper Number. Please try again.", ephemeral=True)
                else: await interaction.send("Invalid Paper Number. Please try again.", ephemeral=True)
            
            elif programme == "A-Level":
                if pn_validation == 1:
                    if paper_number <= "6" and paper_number != "0":
                        if al_validation:
                            subject_name = ciealsubjectsdata.get(subject_code)
                            if in_validation:
                                if ranses == "s":
                                    sesh = "June"
                                elif ranses == "w":
                                    sesh = "November"
                                else:
                                    sesh = "March"
                                    ranvar = "2"
                                qpcode = f"{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}"
                                url = f"https://edupapers.store/wp-content/uploads/simple-file-list/CIE/{programme}/{subject_name}-{subject_code}/{ranyear}/{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}.pdf"
                                qpurl = pyshorteners.Shortener().tinyurl.short(f"https://edupapers.store/wp-content/uploads/simple-file-list/CIE/{programme}/{subject_name}-{subject_code}/{ranyear}/{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}.pdf")
                                msurl = pyshorteners.Shortener().tinyurl.short(f"https://edupapers.store/wp-content/uploads/simple-file-list/CIE/{programme}/{subject_name}-{subject_code}/{ranyear}/{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_ms_{paper_number}{ranvar}.pdf")
                                inurl = pyshorteners.Shortener().tinyurl.short(f"https://edupapers.store/wp-content/uploads/simple-file-list/CIE/{programme}/{subject_name}-{subject_code}/{ranyear}/{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_in_{paper_number}{ranvar}.pdf")
                                embed = discord.Embed(title=f"Random Paper Chosen", description=f"`{qpcode}` has been chosen at random. Below are links to the question paper, marking scheme and the insert.\n\n**QP LINK**: {qpurl}\n**MS LINK**: {msurl}\n**INSERT LINK**: {inurl}", color=0xf4b6c2)
                                await interaction.send(embed=embed)
                            else:
                                if ranses == "s":
                                    sesh = "June"
                                elif ranses == "w":
                                        sesh = "November"
                                else:
                                    sesh = "March"
                                    ranvar = "2"
                                qpcode = f"{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}"
                                qpurl = pyshorteners.Shortener().tinyurl.short(f"https://edupapers.store/wp-content/uploads/simple-file-list/CIE/{programme}/{subject_name}-{subject_code}/{ranyear}/{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_qp_{paper_number}{ranvar}.pdf")
                                msurl = pyshorteners.Shortener().tinyurl.short(f"https://edupapers.store/wp-content/uploads/simple-file-list/CIE/{programme}/{subject_name}-{subject_code}/{ranyear}/{sesh}/{subject_code}_{ranses}{ranyear[2:5]}_ms_{paper_number}{ranvar}.pdf")
                                embed = discord.Embed(title=f"Random Paper Chosen", description=f"`{qpcode}` has been chosen at random. Below are links to the question paper and marking scheme.\n\n**QP LINK**: {qpurl}\n**MS LINK**: {msurl}", color=0xf4b6c2)
                                await interaction.send(embed=embed)  
                        else: await interaction.send("Invalid Subject Code. Please try again.", ephemeral=True)
                    else: await interaction.send("Invalid Paper Number. Please try again.", ephemeral=True)
                else: await interaction.send("Invalid Paper Number. Please try again.", ephemeral=True)
