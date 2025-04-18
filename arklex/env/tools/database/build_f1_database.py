import sqlite3
import argparse
from pathlib import Path
import os


def build_f1_database(folder_path):
    db_path = Path(folder_path) / "formula1_db.sqlite"
    print(db_path)
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
        CREATE TABLE driver (
            id TEXT PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            nationality TEXT,
            team TEXT,
            car_number INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE team (
            id TEXT PRIMARY KEY,
            name TEXT,
            base_country TEXT,
            principal_name TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE race (
            id TEXT PRIMARY KEY,
            name TEXT,
            circuit_name TEXT,
            date DATE,
            season INTEGER,
            round INTEGER
        )
    ''')

    # Updated 2024 Drivers
    drivers = [
        ("drv_1", "Max", "Verstappen", "Netherlands", "Red Bull Racing Honda RBPT", 1),
        ("drv_2", "Lando", "Norris", "United Kingdom", "McLaren Mercedes", 4),
        ("drv_3", "Charles", "Leclerc", "Monaco", "Ferrari", 16),
        ("drv_4", "Oscar", "Piastri", "Australia", "McLaren Mercedes", 81),
        ("drv_5", "Carlos", "Sainz Jr.", "Spain", "Ferrari", 55),
        ("drv_6", "George", "Russell", "United Kingdom", "Mercedes", 63),
        ("drv_7", "Lewis", "Hamilton", "United Kingdom", "Mercedes", 44),
        ("drv_8", "Sergio", "Pérez", "Mexico", "Red Bull Racing Honda RBPT", 11),
        ("drv_9", "Fernando", "Alonso", "Spain", "Aston Martin Aramco Mercedes", 14),
        ("drv_10", "Pierre", "Gasly", "France", "Alpine Renault", 10),
        ("drv_11", "Nico", "Hülkenberg", "Germany", "Haas Ferrari", 27),
        ("drv_12", "Yuki", "Tsunoda", "Japan", "RB Honda RBPT", 22),
        ("drv_13", "Lance", "Stroll", "Canada", "Aston Martin Aramco Mercedes", 18),
        ("drv_14", "Esteban", "Ocon", "France", "Alpine Renault", 31),
        ("drv_15", "Kevin", "Magnussen", "Denmark", "Haas Ferrari", 20),
        ("drv_16", "Alexander", "Albon", "Thailand", "Williams Mercedes", 23),
        ("drv_17", "Daniel", "Ricciardo", "Australia", "RB Honda RBPT", 3),
        ("drv_18", "Oliver", "Bearman", "United Kingdom", "Haas Ferrari", 87),
        ("drv_19", "Franco", "Colapinto", "Argentina", "Williams Mercedes", 43),
        ("drv_20", "Zhou", "Guanyu", "China", "Kick Sauber Ferrari", 24),
        ("drv_21", "Liam", "Lawson", "New Zealand", "RB Honda RBPT", 30),
        ("drv_22", "Valtteri", "Bottas", "Finland", "Kick Sauber Ferrari", 77),
        ("drv_23", "Logan", "Sargeant", "United States", "Williams Mercedes", 2),
        ("drv_24", "Jack", "Doohan", "Australia", "Alpine Renault", 61),
    ]
    
    # 2024 F1 Teams
    teams = [
        ("team_1", "McLaren Mercedes", "UK", "Andrea Stella"),
        ("team_2", "Ferrari", "Italy", "Frédéric Vasseur"),
        ("team_3", "Red Bull Racing Honda RBPT", "Austria", "Christian Horner"),
        ("team_4", "Mercedes", "Germany", "Toto Wolff"),
        ("team_5", "Aston Martin Aramco Mercedes", "UK", "Mike Krack"),
        ("team_6", "Alpine Renault", "France", "Bruno Famin"),
        ("team_7", "Haas Ferrari", "USA", "Ayao Komatsu"),
        ("team_8", "RB Honda RBPT", "Italy", "Laurent Mekies"),
        ("team_9", "Williams Mercedes", "UK", "James Vowles"),
        ("team_10", "Kick Sauber Ferrari", "Switzerland", "Alessandro Alunni Bravi"),
    ]

    # Updated 2024 Race Data (with circuit_name instead of circuit_id)
    races = [
        ("race_1", "Bahrain Grand Prix", "Bahrain International Circuit", "2024-03-02", 2024, 1),
        ("race_2", "Saudi Arabian Grand Prix", "Jeddah Street Circuit", "2024-03-09", 2024, 2),
        ("race_3", "Australian Grand Prix", "Albert Park", "2024-03-24", 2024, 3),
        ("race_4", "Japanese Grand Prix", "Suzuka Circuit", "2024-04-07", 2024, 4),
        ("race_5", "Chinese Grand Prix", "Shanghai International Circuit", "2024-04-21", 2024, 5),
        ("race_6", "Miami Grand Prix", "Miami International Autodrome", "2024-05-05", 2024, 6),
        ("race_7", "Emilia-Romagna Grand Prix", "Imola", "2024-05-19", 2024, 7),
        ("race_8", "Monaco Grand Prix", "Circuit de Monaco", "2024-05-26", 2024, 8),
        ("race_9", "Canadian Grand Prix", "Circuit Gilles Villeneuve", "2024-06-09", 2024, 9),
        ("race_10", "Spanish Grand Prix", "Circuit de Barcelona-Catalunya", "2024-06-23", 2024, 10),
        ("race_11", "Austrian Grand Prix", "Red Bull Ring", "2024-06-30", 2024, 11),
        ("race_12", "British Grand Prix", "Silverstone Circuit", "2024-07-07", 2024, 12),
        ("race_13", "Hungarian Grand Prix", "Hungaroring", "2024-07-21", 2024, 13),
        ("race_14", "Belgian Grand Prix", "Circuit de Spa-Francorchamps", "2024-07-28", 2024, 14),
        ("race_15", "Dutch Grand Prix", "Circuit Zandvoort", "2024-08-25", 2024, 15),
        ("race_16", "Italian Grand Prix", "Monza Circuit", "2024-09-01", 2024, 16),
        ("race_17", "Azerbaijan Grand Prix", "Baku City Circuit", "2024-09-15", 2024, 17),
        ("race_18", "Singapore Grand Prix", "Marina Bay Street Circuit", "2024-09-22", 2024, 18),
        ("race_19", "United States Grand Prix", "Circuit of the Americas", "2024-10-20", 2024, 19),
        ("race_20", "Mexican Grand Prix", "Autódromo Hermanos Rodríguez", "2024-10-27", 2024, 20),
        ("race_21", "Brazilian Grand Prix", "Interlagos", "2024-11-03", 2024, 21),
        ("race_22", "Las Vegas Grand Prix", "Las Vegas Strip Circuit", "2024-11-23", 2024, 22),
        ("race_23", "Qatar Grand Prix", "Lusail International Circuit", "2024-12-01", 2024, 23),
        ("race_24", "Abu Dhabi Grand Prix", "Yas Marina Circuit", "2024-12-08", 2024, 24),
    ]


    cursor.executemany("INSERT INTO driver VALUES (?, ?, ?, ?, ?, ?)", drivers)
    cursor.executemany("INSERT INTO team VALUES (?, ?, ?, ?)", teams)
    cursor.executemany("INSERT INTO race VALUES (?, ?, ?, ?, ?, ?)", races)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder_path", required=True, type=str, help="Location to save the F1 database")
    args = parser.parse_args()

    if not os.path.exists(args.folder_path):
        os.makedirs(args.folder_path)

    build_f1_database(args.folder_path)
