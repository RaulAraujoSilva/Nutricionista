import sqlite3

def limpar_banco():
    conn = sqlite3.connect('nutrition.db')
    cursor = conn.cursor()
    
    # Remove todos os registros
    cursor.execute('DELETE FROM alimentos')
    
    # Reseta o contador de autoincremento
    cursor.execute('DELETE FROM sqlite_sequence WHERE name="alimentos"')
    
    conn.commit()
    conn.close()
    
    print("Banco de dados limpo com sucesso!")

if __name__ == "__main__":
    limpar_banco() 