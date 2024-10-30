from flask import Flask, request, render_template
import pandas as pd

app = Flask(__name__)

# Path to the Excel file
file_path = 'C:/Users/felip/OneDrive/Área de Trabalho/Project/DB_boardgames.xlsx'
df = pd.read_excel(file_path)

# Mappings for game weight and categories
gameweight_map = {
    'basic': (0, 2),
    'intermediate': (2, 3),
    'advanced': (3, 5)
}

category_map = {
    'party': 'Cat:Party',
    'strategy': 'Cat:Strategy',
    'war': 'Cat:War',
    'family': 'Cat:Family',
    'abstract': 'Cat:Abstract'
}


@app.route('/')
def index():
    # Render the HTML form
    return render_template('form2.html')

@app.route('/filter', methods=['POST'])
def filter_games():
    # Get data from the form
    maxplayers = int(request.form['maxplayers'])
    maxplaytime = int(request.form['maxplaytime'])
    gameweight = request.form['gameweight'].lower().strip()
    category = request.form['category'].lower().strip()

    try:
        # Extract corresponding weight range and category column
        gameweightmin, gameweightmax = gameweight_map[gameweight]
        category_column = category_map[category]

        # Filter and sort the DataFrame
        filtered_games = (
            df[
                (df[category_column] == 1) &
                (df['GameWeight'].between(gameweightmin, gameweightmax)) &
                (df['MaxPlayers'] >= maxplayers) &
                (df['ComMaxPlaytime'] <= maxplaytime)
            ]
            .sort_values(by='Rank:boardgame', ascending=True)
            .head(10)[['Name', 'GameWeight', 'MinPlayers', 'MaxPlayers','ComMaxPlaytime', 'Rank:boardgame', 'ImagePath','ShopLink']]
        )

        # Start building the table HTML with inline CSS styles
        table_html = """
        <style>
            table {
                width: 80%;
                margin: 20px auto;
                border-collapse: collapse;
                font-family: Helvetica , sans-serif;
                text-align: center;
            }
            th, td {
                padding: 12px;
                border: 1px solid #ddd;
            }
            th {
                background-color: #f2f2f2;
            }
            tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            img {
                width: 100px;
            }
        </style>
        <table>
        <tr>
            <th>Name</th>
            <th>Game Weight (0-5)</th>
            <th>Min Players</th>
            <th>Max Players</th>
            <th>Play Time (minutes)</th>
            <th>Rank</th>
            <th>Shop</th>
            <th>Image</th>
        </tr>
        """

        # Add rows to the table
        for index, row in filtered_games.iterrows():
            table_html += f"""
            <tr>
                <td>{row['Name']}</td>
                <td>{row['GameWeight']:.1f}</td>
                <td>{row['MinPlayers']}</td>
                <td>{row['MaxPlayers']}</td>
                <td>{row['ComMaxPlaytime']}</td>            
                <td>{int(row['Rank:boardgame'])}</td>
                <td>
                <a href="{row['ShopLink']}" target="_blank">Shop Amazon</a></td>
                <td><img src='{row['ImagePath']}' alt='Game Image'></td>
            </tr>
            """

        table_html += "</table>"

        return table_html

    except KeyError:
        return "Invalid difficulty or category selected. Please try again."

if __name__ == '__main__':
    app.run(debug=True)
