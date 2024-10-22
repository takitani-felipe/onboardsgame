from flask import Flask, request, render_template
import pandas as pd

app = Flask(__name__)

# Path to the Excel file
file_path = './data/DB_boardgames.xlsx'
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
            .head(5)[['Name', 'GameWeight', 'MinPlayers', 'MaxPlayers','ComMaxPlaytime', 'Rank:boardgame', 'ImagePath']]
        )

        num_results = len(filtered_games)
        print(num_results)

        # Start building the table HTML with inline CSS styles
        table_html = f"""
        <link rel="stylesheet" href="./static/style.css">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/css/all.min.css" integrity="sha512-Kc323vGBEqzTmouAECnVceyQqyqdsSiqLQISBL29aUW4U/M7pSPA/gEUZQqv1cwx4OnYxTxve5UMg5GT6L4JJg==" crossorigin="anonymous" referrerpolicy="no-referrer" />
        <div class="results-container">
        <h2 class="results-heading">Results: {num_results} game(s) found</h2>
        """

        # Add rows to the table
        for index, row in filtered_games.iterrows():
            table_html += f"""
                <div class="game-container">
                <div class="image-name">
                <img class="game-image" src='{row['ImagePath']}' width="200" alt='Game Image'>
                </div>
                <div class="game-details">
                <h1>{row['Name']}</h1>
                <p><i class="fa-solid fa-weight-scale"></i> Weight: {row['GameWeight']:.1f}</p>
                <p><i class="fa-solid fa-user"></i> Players: {row.MinPlayers} - {row.MaxPlayers}</p>
                <p><i class="fa-solid fa-clock"></i> Playtime: {row['ComMaxPlaytime']}</p>            
                <p><i class="fa-solid fa-ranking-star"></i> Rank: {int(row['Rank:boardgame'])}</p>
                </div>
                </div>
                <p class="divider"></p>
            """

        table_html += "<a href='/' class='back'><i class='fa-solid fa-backward-step'></i> Search for another game</a></div>"

        return table_html

    except KeyError:
        return "Invalid difficulty or category selected. Please try again."

if __name__ == '__main__':
    app.run(debug=True)
