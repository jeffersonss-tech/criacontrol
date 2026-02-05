import sqlite3
import os

def normalize():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    for f in os.listdir(base_dir):
        if f.startswith('data_') and f.endswith('.db'):
            db_path = os.path.join(base_dir, f)
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("UPDATE pesagem SET sexo='Macho' WHERE sexo='M'")
            c.execute("UPDATE pesagem SET sexo='Femea' WHERE sexo='F'")
            c.execute("UPDATE pesagem SET raca='Zebuinos' WHERE raca='Zebu'")
            conn.commit()
            conn.close()
            print("Normalizado:", f)
    
    print("OK!")

if __name__ == "__main__":
    normalize()
