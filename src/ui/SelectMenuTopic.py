from .Select import Select
from .SelectMenuVisibility import SelectMenuVisibility 
import nextcord as discord
from schemas.redis import TempSessionData

topics_for_practice = {
  '0455': [
    'CH 1 - Basic Economic Problem: Choice And The Allocation Of Resources',
    'CH 2 - The Allocation Of Resources: How The Market Works; Market Failure',
    'CH 3 - The Individual As Producer, Consumer And Borrower',
    'CH 4 - The Private Firm As Producer And Employer',
    'CH 5 - Role Of Government In Economy',
    'CH 6 - Economic Indicators',
    'CH 7 - Developed And Developing Economies: Trends In Production, Population And Living Standards',
    'CH 8 - International Aspects'
  ],
  '0606': [
    'CH 1 - SETS',
    'CH 2 - INTERSECTION POINTS',
    'CH 3 - SURDS,INDICES,LOG',
    'CH 4 - FACTOR THEOREM',
    'CH 5 - MATRICES',
    'CH 6 - COORDINATE GEOMETRY',
    'CH 7 - LINEAR LAW',
    'CH 8 - FUNCTIONS, MODOLUS',
    'CH 9 - TRIGONOMETRY',
    'CH 10 - CIRCULAR MEASURE',
    'CH 11 - PERMUTATION AND COMBINATION',
    'CH 12 - BINOMIAL THEOREM',
    'CH 13 - DIFFERENTIATION',
    'CH 14 - INTEGRATION',
    'CH 15 - KINEMATICS',
    'CH 16 - VECTORS',
    'CH 17 - RELATIVE VELOCITY',
    'CH 18 - SEQUENCES AND SERIES'
  ],
  '0607': [
    'CH 6 - Vectors And Transformations',
    'CH 4 - Coordinate Geometry',
    'CH 1 - Number',
    'CH 2 - Algebra',
    'CH 3 - Functions',
    'CH 5 - Geometry',
    'CH 7 - Mensuration',
    'CH 8 - Trigonometry',
    'CH 9 - Sets',
    'CH 10 - Probability',
    'CH 11 - Statistics'
  ],
  '0620': [
    'CH 1 - STATES OF MATTER',
    'CH 2 - SEPARATING SUBSTANCES',
    'CH 3 - ATOMS AND ELEMENTS',
    'CH 4 - ATOMS COMBINING',
    'CH 5 - REACTING MASSES AND CHEMICAL EQUATIONS',
    'CH 6 - USING MOLES',
    'CH 7 - REDOX REACTIONS',
    'CH 8 - ELECTRICITY AND CHEMICAL CHANGES',
    'CH 9 - ENERGY CHANGES AND REVERSIBLE REACTIONS',
    'CH 10 - THE SPEED OF A REACTION',
    'CH 11 - ACIDS AND BASES',
    'CH 12 - THE PERIODIC TABLE',
    'CH 13 - THE BEHAVIOR OF METALS',
    'CH 14 - MAKING USE OF METALS',
    'CH 15 - AIR AND WATER',
    'CH 16 - SOME NON-METALS AND THEIR COMPOUNDS',
    'CH 17 - ORGANIC CHEMISTRY',
    'CH 18 - POLYMERS',
    'CH 19 - IN THE LAB (CHEMICAL TEST& SALT ANALYSIS)'
  ],
  '0580': [
    'CH 1 - DECIMALS',
    'CH 2 - NUMBER FACTS',
    'CH 3 - RATIONAL AND IRRATIONAL NUMBERS',
    'CH 4 - APPROXIMATION AND ESTIMATION',
    'CH 5 - UPPER AND LOWER BOUND',
    'CH 6 - STANDARD FORM',
    'CH 7 - RATIO AND PROPORTION',
    'CH 8 - FOREIGN EXCHANGE',
    'CH 9 - MAP SCALES',
    'CH 10 - PERCENTAGES',
    'CH 11 - SIMPLE AND COMPOUND INTEREST',
    'CH 12 - SPEED,DISTANCE AND TIME',
    'CH 13 - FORMULAEE',
    'CH 14 - BRACKETS AND SYMPLIFYING',
    'CH 15 - LINEAR EQUAETION',
    'CH 16 - SIMULTANEOUS EQUATIONS',
    'CH 17 - FACTORISING',
    'CH 18 - QUADRATIC EQUATIONS',
    'CH 19 - CHANGING THE SUBJECT',
    'CH 20 - VARIATION',
    'CH 21 - INDICES',
    'CH 22 - SOLVING INEQUALITIES',
    'CH 23 - MENSURATION',
    'CH 24 - POLYGONS',
    'CH 25 - PARALLEL LINES',
    'CH 26 - PYTHAGORAS THEOREM',
    'CH 27 - SYMMETRY',
    'CH 28 - SIMILARITY',
    'CH 29 - CONGRUENCE',
    'CH 30 - AREAS & VOLUMES OF SIMILAR SHAPES',
    'CH 31 - CIRCLE THEOREM',
    'CH 32 - CONSTRUCTIONS AND LOCI',
    'CH 33 - TRIGONOMETRY',
    'CH 34 - LINES',
    'CH 35 - PLOTTING CURVES',
    'CH 36 - GRAPHICAL SOLUTION OF EQUATIONS',
    'CH 37 - DISTANCE-TIME GRAPHS',
    'CH 38 - SPEED-TIME GRAPHS',
    'CH 39 - SETS',
    'CH 40 - VECTORS',
    'CH 41 - MATRICES',
    'CH 42 - TRANSFORMATOIN',
    'CH 43 - STATISTICS',
    'CH 44 - PROBABILITY',
    'CH 45 - FUNCTIONS',
    'CH 47 - LINEAR PROGRAMMING',
    'CH 48 - SEQUENCES',
    'CH 49 - ANGLES',
    'CH 50 - NET',
    'CH 51 - DIFFERENIATION'
  ],
  '0625': [
    'CH 1 - MEASUREMENTS AND UNITS',
    'CH 4 - FORCES AND ENERGY',
    'CH 3 - FORCES AND PRESSURE',
    'CH 5 - THERMAL EFFECTS',
    'CH 2 - FORCES AND MOTION',
    'CH 7 - RAYS AND WAVES',
    'CH 9 - MAGNETS AND CURRENTS',
    'CH 10 - ELECTRON AND ELECTRONICS',
    'CH 6 - WAVES AND SOUNDS',
    'CH 8 - ELECTRICITY',
    'CH 11 - ATOMS AND RADIOACTIVITY'
  ],
  '0610': [
    'CH 1 - CHARACTERISTICS AND CLASSIFICATION OF LIVING ORGANISMS',
    'CH 2 - ORGANIZATION AND MAINTENANCE OF THE ORGANISM',
    'CH 3 - MOVEMENT IN AND OUT OF CELLS',
    'CH 4 - BIOLOGICAL MOLECULES',
    'CH 5 - ENZYMES',
    'CH 6 - PLANT NUTRITION',
    'CH 7 - HUMAN NUTRITION',
    'CH 8 - TRANSPORT IN PLANTS',
    'CH 9 - TRANSPORT IN ANIMALS',
    'CH 10 - DISEASES AND IMMUNITY',
    'CH 11 - GAS EXCHANGE IN HUMANS',
    'CH 12 - RESPIRATION',
    'CH 13 - EXCRETION IN HUMANS',
    'CH 14 - CO-ORDINATION AND RESPONSE',
    'CH 15 - DRUGS',
    'CH 16 - REPRODUCTION',
    'CH 17 - INHERITANCE',
    'CH 18 - VARIATION AND SELECTION',
    'CH 19 - ORGANISMS AND THEIR ENVIRONMENT',
    'CH 20 - BIOTECHNOLOGY AND GENETIC ENGINEERING',
    'CH 21 - HUMAN INFLUENCES ON ECOSYSTEMS'
  ],
  '0417': [
    'CH 1 - Types And Components Of Computer Systems',
    'CH 2 - Input And Output Devices',
    'CH 3 - Storage Devices And Media',
    'CH 4 - Networks And The Effects Of Using Them',
    'CH 5 - The Effects Of Using IT',
    'CH 6 - ICT Applications',
    'CH 7 - The Systems Life Cycle',
    'CH 8 - Safety And Security',
    'CH 9 - Audience',
    'CH 10 - Communication',
    'CH 11 - File Management',
    'CH 12 - Images',
    'CH 13 - Layout',
    'CH 14 - Styles',
    'CH 15 - Proofing',
    'CH 16 - Graphs And Charts',
    'CH 17 - Document Production',
    'CH 18 - Data Manipulation',
    'CH 19 - Presentations',
    'CH 20 - Data Analysis',
    'CH 21 - Website Authoring'
  ]
}


class SelectMenuTopic(discord.ui.View):
    def __init__(self, interaction: discord.Interaction):
        super().__init__(timeout=300)
        tempdata = TempSessionData.get(interaction.user.id)
        topics = topics_for_practice[tempdata["subject"]]
        if len(topics) > 25:
            for i in range(len(topics) // 25):
                self.topic = Select(
                    name="topics",
                    placeholder=f"Choose a topic (menu {i+1})",
                    options=list(map(lambda x: discord.SelectOption(label=x, value=x), topics[i*25:(i+1)*25])),
                    max_values=25
                )
                self.add_item(self.topic)
        else:
            self.topic = Select(
                name="topics",
                placeholder="Choose a topic",
                options=list(map(lambda x: discord.SelectOption(label=x, value=x), topics)),
                max_values=len(topics)
            )
            self.add_item(self.topic)

        self.continue_button = discord.ui.Button(label="Continue", style=discord.ButtonStyle.green)
        async def continue_callback(interaction: discord.Interaction):
            self.stop()

        self.cancel_button = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.red)
        async def cancel_callback(interaction: discord.Interaction):
            await interaction.edit(content="Cancelled!", view=None)
            TempSessionData.delete(str(interaction.user.id))

        self.continue_button.callback = continue_callback
        self.cancel_button.callback = cancel_callback

        self.add_item(self.continue_button)
        self.add_item(self.cancel_button)