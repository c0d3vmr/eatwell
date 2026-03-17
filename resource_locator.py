"""
Phase 3: Geographic & Financial Mapping
ResourceLocator function with synthetic store data and travel feasibility.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
from user_context import UserContext, Logistics


class StoreType(Enum):
    GROCERY = "grocery"
    FOOD_PANTRY = "food_pantry"
    FARMERS_MARKET = "farmers_market"
    DISCOUNT = "discount"
    SPECIALTY = "specialty"


class InventoryLevel(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Store:
    """Represents a nearby store/resource."""
    name: str
    store_type: StoreType
    distance_miles: float
    snap_accepted: bool
    wic_accepted: bool
    inventory_level: InventoryLevel
    price_tier: int  # 1=cheapest, 5=most expensive
    specialty_items: List[str] = field(default_factory=list)
    hours: str = "9am-9pm"
    latitude: float = 0.0  # For map visualization
    longitude: float = 0.0  # For map visualization
    
    @property
    def is_food_assistance_friendly(self) -> bool:
        return self.snap_accepted or self.wic_accepted


@dataclass
class TravelFeasibility:
    """Calculated travel feasibility for a store."""
    store: Store
    is_accessible: bool
    travel_method: str  # "walk", "transit", "drive"
    estimated_time_minutes: int
    accessibility_score: float  # 0-1, higher is better
    notes: List[str] = field(default_factory=list)
    transit_cost: float = 0.0  # Public transit fare if applicable


@dataclass
class ResourceMap:
    """Complete resource mapping for a user."""
    user_zip: str
    accessible_stores: List[TravelFeasibility]
    food_pantries: List[TravelFeasibility]
    snap_stores: List[TravelFeasibility]
    all_stores: List[Store]


# Synthetic store database - simulates real-world data
# Organized by zip code prefix for demo purposes
# Base coordinates: Atlanta area (33.749, -84.388) for demo
SYNTHETIC_STORES_DATABASE: Dict[str, List[Store]] = {
    "default": [
        Store(
            name="SaveMart Grocery",
            store_type=StoreType.GROCERY,
            distance_miles=1.2,
            snap_accepted=True,
            wic_accepted=True,
            inventory_level=InventoryLevel.HIGH,
            price_tier=3,
            specialty_items=["organic produce", "gluten-free"],
            hours="7am-10pm",
            latitude=33.758,
            longitude=-84.380
        ),
        Store(
            name="Community Food Pantry",
            store_type=StoreType.FOOD_PANTRY,
            distance_miles=0.8,
            snap_accepted=False,  # Free food
            wic_accepted=False,
            inventory_level=InventoryLevel.MEDIUM,
            price_tier=1,  # Free
            specialty_items=["canned goods", "bread", "produce"],
            hours="Mon/Wed/Fri 10am-2pm",
            latitude=33.754,
            longitude=-84.392
        ),
        Store(
            name="Budget Foods",
            store_type=StoreType.DISCOUNT,
            distance_miles=2.5,
            snap_accepted=True,
            wic_accepted=False,
            inventory_level=InventoryLevel.HIGH,
            price_tier=1,
            specialty_items=["bulk items", "frozen foods"],
            hours="8am-9pm",
            latitude=33.765,
            longitude=-84.410
        ),
        Store(
            name="Fresh Farmers Market",
            store_type=StoreType.FARMERS_MARKET,
            distance_miles=1.8,
            snap_accepted=True,
            wic_accepted=True,
            inventory_level=InventoryLevel.MEDIUM,
            price_tier=2,
            specialty_items=["local produce", "eggs", "honey"],
            hours="Sat 8am-1pm",
            latitude=33.742,
            longitude=-84.375
        ),
        Store(
            name="Whole Health Foods",
            store_type=StoreType.SPECIALTY,
            distance_miles=3.2,
            snap_accepted=False,
            wic_accepted=False,
            inventory_level=InventoryLevel.HIGH,
            price_tier=5,
            specialty_items=["supplements", "organic", "specialty diet"],
            hours="9am-8pm",
            latitude=33.770,
            longitude=-84.365
        ),
        Store(
            name="Dollar General",
            store_type=StoreType.DISCOUNT,
            distance_miles=0.5,
            snap_accepted=True,
            wic_accepted=False,
            inventory_level=InventoryLevel.LOW,
            price_tier=2,
            specialty_items=["canned goods", "snacks", "basic staples"],
            hours="8am-10pm",
            latitude=33.751,
            longitude=-84.385
        ),
        Store(
            name="St. Mary's Food Bank",
            store_type=StoreType.FOOD_PANTRY,
            distance_miles=2.1,
            snap_accepted=False,
            wic_accepted=False,
            inventory_level=InventoryLevel.HIGH,
            price_tier=1,
            specialty_items=["fresh produce", "meat", "dairy"],
            hours="Tue/Thu 9am-3pm",
            latitude=33.738,
            longitude=-84.405
        ),
        Store(
            name="ALDI",
            store_type=StoreType.DISCOUNT,
            distance_miles=4.0,
            snap_accepted=True,
            wic_accepted=True,
            inventory_level=InventoryLevel.HIGH,
            price_tier=1,
            specialty_items=["produce", "dairy", "frozen", "specialty imports"],
            hours="9am-8pm",
            latitude=33.780,
            longitude=-84.420
        ),
        Store(
            name="Target",
            store_type=StoreType.GROCERY,
            distance_miles=5.5,
            snap_accepted=True,
            wic_accepted=True,
            inventory_level=InventoryLevel.HIGH,
            price_tier=3,
            specialty_items=["organic", "fresh produce", "supplements"],
            hours="8am-10pm",
            latitude=33.795,
            longitude=-84.360
        ),
        Store(
            name="Neighborhood Co-op",
            store_type=StoreType.SPECIALTY,
            distance_miles=1.5,
            snap_accepted=True,
            wic_accepted=False,
            inventory_level=InventoryLevel.MEDIUM,
            price_tier=4,
            specialty_items=["local", "organic", "bulk bins", "specialty"],
            hours="10am-7pm",
            latitude=33.745,
            longitude=-84.395
        )
    ],
    # Additional zip-code-specific stores can be added here
    "303": [  # Denver area example
        Store(
            name="King Soopers",
            store_type=StoreType.GROCERY,
            distance_miles=1.0,
            snap_accepted=True,
            wic_accepted=True,
            inventory_level=InventoryLevel.HIGH,
            price_tier=3,
            specialty_items=["organic", "deli", "pharmacy"],
            hours="6am-11pm"
        ),
    ],
    "300": [  # Atlanta area example
        Store(
            name="Publix",
            store_type=StoreType.GROCERY,
            distance_miles=1.3,
            snap_accepted=True,
            wic_accepted=True,
            inventory_level=InventoryLevel.HIGH,
            price_tier=3,
            specialty_items=["deli", "bakery", "organic"],
            hours="7am-10pm"
        ),
    ]
}

# ZIP code coordinates for Houston metro area
# Format: "zip_code": (latitude, longitude)
# This app is designed for Houston, TX
ZIP_CODE_COORDINATES: Dict[str, tuple] = {
    # ===== DOWNTOWN & CENTRAL HOUSTON =====
    "77001": (29.7545, -95.3537),   # Downtown Houston
    "77002": (29.7565, -95.3596),   # Downtown Houston
    "77003": (29.7409, -95.3457),   # East Downtown
    "77004": (29.7243, -95.3657),   # Third Ward / Museum District
    "77005": (29.7174, -95.4219),   # West University
    "77006": (29.7390, -95.3934),   # Montrose
    "77007": (29.7731, -95.4127),   # Heights / Washington Ave
    "77008": (29.7905, -95.4170),   # Heights
    "77009": (29.7957, -95.3721),   # Northside / Near Heights
    "77010": (29.7545, -95.3537),   # Downtown
    "77011": (29.7329, -95.3027),   # East End
    "77012": (29.7129, -95.2798),   # Harrisburg / Manchester
    "77013": (29.7769, -95.2580),   # Denver Harbor
    "77014": (29.9772, -95.4855),   # Champions area
    "77015": (29.7626, -95.1811),   # Channelview
    "77016": (29.8515, -95.2917),   # Kashmere Gardens
    "77017": (29.6865, -95.2569),   # Park Place / South Houston
    "77018": (29.8291, -95.4270),   # Oak Forest / Garden Oaks
    "77019": (29.7580, -95.4147),   # River Oaks / Montrose
    "77020": (29.7766, -95.3124),   # Fifth Ward / Denver Harbor
    "77021": (29.7037, -95.3590),   # South Park / Third Ward
    "77022": (29.8282, -95.3718),   # Independence Heights
    "77023": (29.7185, -95.3138),   # Eastwood / Magnolia Park
    "77024": (29.7749, -95.5249),   # Memorial Villages
    "77025": (29.6901, -95.4290),   # Braeswood Place
    "77026": (29.8009, -95.3194),   # Kashmere / Trinity Gardens
    "77027": (29.7396, -95.4386),   # Galleria / Uptown
    "77028": (29.8334, -95.2857),   # Trinity / Houston Gardens
    "77029": (29.7569, -95.2288),   # Cloverleaf
    "77030": (29.7068, -95.3973),   # Texas Medical Center
    "77031": (29.6582, -95.5396),   # Westwood / Sharpstown
    "77032": (29.9503, -95.3145),   # North Houston / IAH area
    "77033": (29.6687, -95.3242),   # South Park
    "77034": (29.6168, -95.1988),   # Ellington / Southeast
    "77035": (29.6616, -95.4732),   # Meyerland / Willowbend
    "77036": (29.7003, -95.5378),   # Sharpstown / Chinatown
    "77037": (29.8851, -95.4109),   # Northline / Aldine
    "77038": (29.9189, -95.4398),   # North Houston / Aldine
    "77039": (29.9037, -95.3397),   # North Houston / Aldine
    "77040": (29.8687, -95.5365),   # Northwest Crossing
    "77041": (29.8601, -95.5850),   # Jersey Village area
    "77042": (29.7318, -95.5593),   # Westchase / Briargrove
    "77043": (29.7900, -95.5547),   # Spring Branch West
    "77044": (29.8475, -95.1742),   # Northeast Houston / Sheldon
    "77045": (29.6236, -95.4400),   # South Acres / Crestmont Park
    "77046": (29.7333, -95.4450),   # Galleria area
    "77047": (29.5958, -95.3747),   # Sunnyside
    "77048": (29.6057, -95.3175),   # South Houston / Hobby area
    "77049": (29.8191, -95.1432),   # Cloverleaf / Sheldon
    "77050": (29.9169, -95.2805),   # North Houston
    "77051": (29.6512, -95.3869),   # South Park / Sunnyside
    "77053": (29.5829, -95.4787),   # Fort Bend / Fondren SW
    "77054": (29.6850, -95.3968),   # Texas Medical Center area
    "77055": (29.7894, -95.4785),   # Spring Branch
    "77056": (29.7496, -95.4621),   # Galleria
    "77057": (29.7476, -95.4855),   # Tanglewood / Galleria
    "77058": (29.5581, -95.0924),   # NASA / Clear Lake
    "77059": (29.5849, -95.1122),   # Clear Lake / Nassau Bay
    "77060": (29.9218, -95.3914),   # North Houston / Greenspoint
    "77061": (29.6603, -95.2632),   # Golfcrest / South Houston
    "77062": (29.5676, -95.1350),   # Clear Lake
    "77063": (29.7202, -95.5128),   # Sharpstown
    "77064": (29.9206, -95.5422),   # Cypress Station
    "77065": (29.9310, -95.5870),   # Cypress area
    "77066": (29.9580, -95.4881),   # Champions / Willowbrook
    "77067": (29.9418, -95.4442),   # FM 1960 area
    "77068": (29.9689, -95.5137),   # Champions Forest
    "77069": (29.9793, -95.5362),   # Champions area
    "77070": (29.9623, -95.5849),   # Cypress Creek
    "77071": (29.6481, -95.5185),   # Fondren Southwest
    "77072": (29.6954, -95.5871),   # Alief
    "77073": (29.9700, -95.3769),   # North Houston / Aldine
    "77074": (29.6842, -95.5125),   # Sharpstown / Fondren
    "77075": (29.6222, -95.2651),   # Ellington Field area
    "77076": (29.8569, -95.3520),   # North Houston / Acres Homes
    "77077": (29.7547, -95.6114),   # Energy Corridor
    "77078": (29.8461, -95.2475),   # Sheldon / Barrett
    "77079": (29.7734, -95.5976),   # Memorial West
    "77080": (29.8161, -95.5252),   # Spring Branch North
    "77081": (29.7116, -95.4652),   # Bellaire / Meyerland
    "77082": (29.7249, -95.6428),   # Westchase / Mission Bend
    "77083": (29.6835, -95.6458),   # Mission Bend / Alief
    "77084": (29.8236, -95.6632),   # West Houston / Bear Creek
    "77085": (29.6150, -95.4890),   # Southwest Houston
    "77086": (29.9010, -95.4758),   # North Houston / Greenspoint
    "77087": (29.6869, -95.2998),   # South Houston / Park Place
    "77088": (29.8694, -95.3990),   # Acres Homes
    "77089": (29.5848, -95.2277),   # Southeast Houston / Pearland
    "77090": (29.9802, -95.4609),   # FM 1960 / Champions
    "77091": (29.8361, -95.4503),   # Inwood / Acres Homes
    "77092": (29.8233, -95.4793),   # Spring Branch
    "77093": (29.8501, -95.3261),   # Aldine area
    "77094": (29.7729, -95.6712),   # Energy Corridor West
    "77095": (29.8898, -95.6481),   # Bear Creek / Copperfield
    "77096": (29.6726, -95.4781),   # Meyerland / Fondren
    "77098": (29.7335, -95.4143),   # Upper Kirby / Montrose
    "77099": (29.6703, -95.5803),   # Alief
    
    # ===== SURROUNDING AREAS (Greater Houston) =====
    "77301": (30.3116, -95.4560),   # Conroe
    "77302": (30.2074, -95.4073),   # Conroe area
    "77303": (30.3490, -95.5310),   # Conroe area
    "77304": (30.3116, -95.5200),   # Conroe
    "77306": (30.4218, -95.4560),   # Conroe area
    "77336": (30.0472, -95.1372),   # Huffman
    "77338": (30.0102, -95.2669),   # Humble
    "77339": (30.0458, -95.2063),   # Kingwood
    "77345": (30.0552, -95.1873),   # Kingwood
    "77346": (29.9980, -95.1580),   # Atascocita
    "77354": (30.1800, -95.5500),   # Magnolia
    "77355": (30.1270, -95.6850),   # Magnolia
    "77356": (30.3730, -95.6440),   # Montgomery
    "77357": (30.0850, -95.4200),   # New Caney
    "77362": (30.1420, -95.6200),   # Pinehurst
    "77365": (30.1640, -95.2880),   # Porter
    "77373": (30.0290, -95.4070),   # Spring
    "77375": (30.0790, -95.5450),   # Tomball
    "77377": (30.0780, -95.6200),   # Tomball
    "77379": (30.0040, -95.5290),   # Spring / Klein
    "77380": (30.1610, -95.4560),   # The Woodlands
    "77381": (30.1770, -95.4890),   # The Woodlands
    "77382": (30.2000, -95.5170),   # The Woodlands
    "77384": (30.2190, -95.4750),   # The Woodlands
    "77385": (30.1360, -95.4150),   # The Woodlands
    "77386": (30.0970, -95.3770),   # Spring
    "77388": (30.0120, -95.4680),   # Spring
    "77389": (30.0620, -95.5130),   # Spring / Klein
    
    # ===== KATY / WEST HOUSTON =====
    "77401": (29.7063, -95.4077),   # Bellaire
    "77406": (29.6960, -95.7640),   # Richmond
    "77407": (29.7170, -95.7560),   # Richmond
    "77429": (29.9410, -95.6770),   # Cypress
    "77430": (29.3270, -95.5510),   # Damon
    "77433": (29.9610, -95.7070),   # Cypress
    "77447": (30.0110, -95.8170),   # Hockley
    "77449": (29.8270, -95.7330),   # Katy
    "77450": (29.7660, -95.7530),   # Katy
    "77451": (29.6440, -95.8520),   # Fulshear
    "77459": (29.5510, -95.5750),   # Missouri City
    "77461": (29.4960, -95.7590),   # Needville
    "77469": (29.5820, -95.7640),   # Richmond
    "77471": (29.6210, -95.7580),   # Rosenberg
    "77476": (29.6870, -95.9040),   # Sealy
    "77477": (29.6200, -95.5640),   # Stafford
    "77478": (29.5930, -95.6180),   # Sugar Land
    "77479": (29.5580, -95.6340),   # Sugar Land
    "77484": (30.1030, -95.9020),   # Waller
    "77489": (29.5810, -95.5350),   # Missouri City
    "77493": (29.7840, -95.8150),   # Katy
    "77494": (29.7600, -95.8280),   # Katy
    "77498": (29.6130, -95.5720),   # Sugar Land
    
    # ===== PASADENA / SOUTHEAST =====
    "77501": (29.6911, -95.2091),   # Pasadena
    "77502": (29.6680, -95.1680),   # Pasadena
    "77503": (29.6840, -95.1540),   # Pasadena
    "77504": (29.6470, -95.1730),   # Pasadena
    "77505": (29.6280, -95.1340),   # Pasadena
    "77506": (29.7050, -95.1840),   # Pasadena
    "77507": (29.6610, -95.0620),   # Pasadena / Deer Park
    "77508": (29.7180, -95.1460),   # Pasadena
    "77510": (29.3780, -94.9950),   # Santa Fe
    "77511": (29.4190, -95.2680),   # Alvin
    "77512": (29.4240, -95.2430),   # Alvin
    "77514": (29.5120, -94.6440),   # Anahuac
    "77515": (29.1480, -95.4350),   # Angleton
    "77517": (29.3810, -94.9210),   # Santa Fe
    "77518": (29.5130, -94.9840),   # Bacliff
    "77520": (29.7350, -94.9770),   # Baytown
    "77521": (29.7780, -94.9360),   # Baytown
    "77530": (29.7690, -95.1170),   # Channelview
    "77531": (29.0460, -95.4350),   # Clute
    "77532": (29.8400, -95.0710),   # Crosby
    "77533": (30.0520, -94.8570),   # Daisetta
    "77534": (29.3750, -95.1430),   # Danbury
    "77535": (30.0320, -94.6890),   # Dayton
    "77536": (29.7340, -95.1130),   # Deer Park
    "77539": (29.4990, -95.0460),   # Dickinson
    "77546": (29.5170, -95.1760),   # Friendswood
    "77547": (29.7100, -95.1330),   # Galena Park
    "77550": (29.3010, -94.7980),   # Galveston
    "77551": (29.2810, -94.8230),   # Galveston
    "77554": (29.2140, -94.9550),   # Galveston West
    "77560": (29.8070, -94.6760),   # Hankamer
    "77562": (29.6310, -95.0110),   # Highlands
    "77563": (29.3570, -94.9150),   # Hitchcock
    "77565": (29.5000, -95.0160),   # Kemah
    "77566": (29.0320, -95.4050),   # Lake Jackson
    "77568": (29.3610, -95.0780),   # La Marque
    "77571": (29.6700, -95.0560),   # La Porte
    "77573": (29.5440, -95.0930),   # League City
    "77574": (29.5440, -95.0700),   # League City
    "77581": (29.5640, -95.2960),   # Pearland
    "77583": (29.4280, -95.4310),   # Rosharon
    "77584": (29.5150, -95.3390),   # Pearland
    "77586": (29.5740, -95.0430),   # Seabrook
    "77587": (29.6680, -95.2400),   # South Houston
    "77590": (29.3850, -94.9270),   # Texas City
    "77591": (29.4040, -94.9520),   # Texas City
    
    # ===== DEFAULT =====
    "default": (29.7604, -95.3698),   # Houston center
}


def get_base_coordinates(zip_code: str) -> tuple:
    """Get approximate lat/long for a zip code."""
    # Try exact zip code first
    if zip_code in ZIP_CODE_COORDINATES:
        return ZIP_CODE_COORDINATES[zip_code]
    # Try 3-digit prefix
    if len(zip_code) >= 3:
        prefix = zip_code[:3]
        # Check if any zip starts with this prefix
        for zc in ZIP_CODE_COORDINATES.keys():
            if zc.startswith(prefix) and zc != "default":
                return ZIP_CODE_COORDINATES[zc]
    # Default to Houston center
    return ZIP_CODE_COORDINATES["default"]


def get_stores_for_zip(zip_code: str) -> List[Store]:
    """Get stores near a zip code (simulated lookup)."""
    # Check for zip-code-specific stores
    zip_prefix = zip_code[:3] if len(zip_code) >= 3 else zip_code
    
    # Get base coordinates for this zip code
    base_lat, base_lon = get_base_coordinates(zip_code)
    
    # Get default stores and adjust coordinates to the user's location
    default_stores = SYNTHETIC_STORES_DATABASE.get("default", [])
    stores = []
    
    for store in default_stores:
        # Create a copy with adjusted coordinates
        # Offset based on distance (roughly 0.01 degrees ≈ 0.69 miles)
        lat_offset = (store.latitude - 33.749) if store.latitude != 0 else 0
        lon_offset = (store.longitude - (-84.388)) if store.longitude != 0 else 0
        
        adjusted_store = Store(
            name=store.name,
            store_type=store.store_type,
            distance_miles=store.distance_miles,
            snap_accepted=store.snap_accepted,
            wic_accepted=store.wic_accepted,
            inventory_level=store.inventory_level,
            price_tier=store.price_tier,
            specialty_items=store.specialty_items.copy(),
            hours=store.hours,
            latitude=base_lat + lat_offset,
            longitude=base_lon + lon_offset
        )
        stores.append(adjusted_store)
    
    # Add any zip-specific stores
    if zip_prefix in SYNTHETIC_STORES_DATABASE:
        for store in SYNTHETIC_STORES_DATABASE[zip_prefix]:
            lat_offset = (store.latitude - 33.749) if store.latitude != 0 else 0
            lon_offset = (store.longitude - (-84.388)) if store.longitude != 0 else 0
            adjusted_store = Store(
                name=store.name,
                store_type=store.store_type,
                distance_miles=store.distance_miles,
                snap_accepted=store.snap_accepted,
                wic_accepted=store.wic_accepted,
                inventory_level=store.inventory_level,
                price_tier=store.price_tier,
                specialty_items=store.specialty_items.copy(),
                hours=store.hours,
                latitude=base_lat + lat_offset,
                longitude=base_lon + lon_offset
            )
            stores.append(adjusted_store)
    
    return stores


def calculate_travel_time(distance_miles: float, method: str) -> int:
    """Calculate estimated travel time in minutes."""
    speeds = {
        "walk": 3.0,  # mph
        "transit": 12.0,  # mph average including wait
        "drive": 25.0  # mph average with traffic
    }
    speed = speeds.get(method, 3.0)
    base_time = (distance_miles / speed) * 60
    
    # Add overhead
    if method == "transit":
        base_time += 10  # Wait time
    elif method == "walk":
        base_time += 5  # Round trip buffer
    
    return int(base_time)


def calculate_transit_cost(distance_miles: float, method: str) -> float:
    """
    Calculate estimated public transit cost for a round trip.
    
    Cost assumptions (US averages):
    - Walk: Free
    - Transit: $2.50 one-way (typical bus/subway fare), round trip = $5.00
      - Some cities have day passes that are more economical for multiple trips
    - Drive: Gas cost estimated at ~$0.20/mile for fuel
    
    Args:
        distance_miles: One-way distance to store
        method: Travel method ("walk", "transit", "drive")
    
    Returns:
        Estimated round-trip transportation cost
    """
    if method == "walk":
        return 0.0
    elif method == "transit":
        # Typical US bus/subway fare is $1.50-$3.00 one way
        # Using $2.50 as average one-way fare
        base_fare = 2.50
        # Round trip
        return base_fare * 2
    elif method == "drive":
        # Gas cost for round trip (distance * 2 * cost per mile)
        # Average ~$0.20/mile for fuel (varies by vehicle and gas prices)
        return distance_miles * 2 * 0.20
    return 0.0


def calculate_travel_feasibility(store: Store, logistics: Logistics) -> TravelFeasibility:
    """
    Calculate travel feasibility for a specific store based on user logistics.
    """
    notes = []
    
    # Determine best travel method
    if logistics.has_vehicle:
        travel_method = "drive"
        max_practical_distance = 15.0
    elif logistics.has_public_transit:
        travel_method = "transit"
        max_practical_distance = 8.0
    else:
        travel_method = "walk"
        max_practical_distance = 2.0
    
    # Check accessibility
    is_accessible = store.distance_miles <= logistics.max_travel_distance_miles
    
    # If not accessible by preferred method, check alternatives
    if not is_accessible:
        if store.distance_miles <= 2.0:
            travel_method = "walk"
            is_accessible = True
            notes.append("Walking distance")
        elif store.distance_miles <= 8.0 and logistics.has_public_transit:
            travel_method = "transit"
            is_accessible = True
            notes.append("Accessible via public transit")
    
    # Calculate travel time
    travel_time = calculate_travel_time(store.distance_miles, travel_method)
    
    # Calculate transit cost (round trip)
    transit_cost = calculate_transit_cost(store.distance_miles, travel_method)
    
    # Calculate accessibility score
    distance_score = max(0, 1 - (store.distance_miles / max_practical_distance))
    time_score = max(0, 1 - (travel_time / 60))  # Penalize trips over 60 min
    inventory_score = {InventoryLevel.HIGH: 1.0, InventoryLevel.MEDIUM: 0.7, InventoryLevel.LOW: 0.4}[store.inventory_level]
    
    accessibility_score = (distance_score * 0.4 + time_score * 0.3 + inventory_score * 0.3)
    
    # Add notes
    if store.store_type == StoreType.FOOD_PANTRY:
        notes.append("FREE - Food pantry")
    if store.distance_miles <= 1.0:
        notes.append("Very close")
    if travel_time > 45:
        notes.append("Long travel time")
        is_accessible = is_accessible and logistics.grocery_trips_per_week >= 2
    if transit_cost > 0:
        notes.append(f"Transit: ${transit_cost:.2f} round trip")
    
    return TravelFeasibility(
        store=store,
        is_accessible=is_accessible,
        travel_method=travel_method,
        estimated_time_minutes=travel_time,
        accessibility_score=round(accessibility_score, 2),
        notes=notes,
        transit_cost=transit_cost
    )


def resource_locator(user_context: UserContext) -> ResourceMap:
    """
    Main function: Locate and evaluate all nearby resources based on user context.
    
    Args:
        user_context: User's complete context including logistics
        
    Returns:
        ResourceMap with accessible stores, food pantries, and SNAP stores
    """
    # Get all stores for user's zip code
    all_stores = get_stores_for_zip(user_context.logistics.zip_code)
    
    # Calculate travel feasibility for each store
    all_feasibility: List[TravelFeasibility] = []
    for store in all_stores:
        feasibility = calculate_travel_feasibility(store, user_context.logistics)
        all_feasibility.append(feasibility)
    
    # Filter accessible stores
    accessible_stores = [f for f in all_feasibility if f.is_accessible]
    accessible_stores.sort(key=lambda x: (-x.accessibility_score, x.store.distance_miles))
    
    # Filter food pantries
    food_pantries = [f for f in accessible_stores if f.store.store_type == StoreType.FOOD_PANTRY]
    
    # Filter SNAP-accepting stores
    snap_stores = [f for f in accessible_stores if f.store.snap_accepted]
    
    # Prioritize based on user's financial situation
    if user_context.financials.has_assistance:
        # Move SNAP/WIC stores to top
        snap_stores.sort(key=lambda x: (x.store.price_tier, x.store.distance_miles))
    
    return ResourceMap(
        user_zip=user_context.logistics.zip_code,
        accessible_stores=accessible_stores,
        food_pantries=food_pantries,
        snap_stores=snap_stores,
        all_stores=all_stores
    )


def print_resource_map(resource_map: ResourceMap, user_context: UserContext) -> None:
    """Print a formatted resource map."""
    print("\n" + "="*60)
    print("  RESOURCE LOCATOR - Nearby Food Resources")
    print("="*60)
    print(f"\n📍 Location: ZIP {resource_map.user_zip}")
    print(f"🚗 Transportation: {user_context.logistics.mobility_level.upper()}")
    
    # Food Pantries (if budget is low)
    if resource_map.food_pantries and user_context.financials.budget_tier in ["very_low", "low"]:
        print("\n🆓 FREE FOOD PANTRIES:")
        for tf in resource_map.food_pantries[:3]:
            transport_cost = f" | Transit: ${tf.transit_cost:.2f}" if tf.transit_cost > 0 else ""
            print(f"   • {tf.store.name}")
            print(f"     Distance: {tf.store.distance_miles} mi ({tf.travel_method}, ~{tf.estimated_time_minutes} min){transport_cost}")
            print(f"     Hours: {tf.store.hours}")
            print(f"     Items: {', '.join(tf.store.specialty_items[:3])}")
    
    # SNAP-Authorized Stores
    if resource_map.snap_stores and user_context.financials.snap_status:
        print("\n🏪 SNAP-AUTHORIZED STORES:")
        for tf in resource_map.snap_stores[:4]:
            if tf.store.store_type != StoreType.FOOD_PANTRY:
                price_symbol = "$" * tf.store.price_tier
                transport_cost = f" | Transit: ${tf.transit_cost:.2f}" if tf.transit_cost > 0 else ""
                print(f"   • {tf.store.name} [{price_symbol}]")
                print(f"     Distance: {tf.store.distance_miles} mi ({tf.travel_method}){transport_cost}")
                print(f"     Inventory: {tf.store.inventory_level.value}")
    
    # All Accessible Stores
    print("\n📋 ALL ACCESSIBLE STORES (by score):")
    for i, tf in enumerate(resource_map.accessible_stores[:6], 1):
        price_symbol = "FREE" if tf.store.store_type == StoreType.FOOD_PANTRY else "$" * tf.store.price_tier
        snap_marker = " [SNAP]" if tf.store.snap_accepted else ""
        wic_marker = " [WIC]" if tf.store.wic_accepted else ""
        transport_cost = f" | 🚌 ${tf.transit_cost:.2f}" if tf.transit_cost > 0 else ""
        
        print(f"   {i}. {tf.store.name} [{price_symbol}]{snap_marker}{wic_marker}")
        print(f"      Type: {tf.store.store_type.value} | Score: {tf.accessibility_score}")
        print(f"      {tf.store.distance_miles} mi via {tf.travel_method} (~{tf.estimated_time_minutes} min){transport_cost}")
        if tf.notes:
            print(f"      Notes: {', '.join(tf.notes)}")


def get_stores_with_item(resource_map: ResourceMap, item: str) -> List[TravelFeasibility]:
    """Find stores that likely have a specific item."""
    matching_stores = []
    
    # Keywords for different food categories
    item_keywords = {
        "produce": ["produce", "fresh", "farmers", "organic"],
        "spinach": ["produce", "fresh", "organic", "leafy"],
        "eggs": ["eggs", "dairy", "fresh", "farmers"],
        "fish": ["fresh", "specialty", "salmon", "seafood"],
        "salmon": ["fresh", "specialty", "seafood"],
        "beans": ["bulk", "canned", "staples", "basic"],
        "lentils": ["bulk", "specialty", "organic"],
        "nuts": ["bulk", "specialty", "snacks"],
        "supplements": ["supplements", "specialty", "health"],
    }
    
    item_lower = item.lower()
    search_keywords = item_keywords.get(item_lower, [item_lower])
    
    for feasibility in resource_map.accessible_stores:
        store = feasibility.store
        # Check if store might have this item
        store_items = " ".join(store.specialty_items).lower()
        if any(kw in store_items for kw in search_keywords):
            matching_stores.append(feasibility)
        elif store.inventory_level == InventoryLevel.HIGH:
            # High inventory stores likely have most items
            matching_stores.append(feasibility)
    
    return matching_stores
