import os
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
    return render_template('form.html')

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
            .head(10)[['Name', 'GameWeight', 'MinPlayers', 'MaxPlayers','ComMaxPlaytime', 'Rank:boardgame', 'ImagePath', 'ShopLink']]
        )

        num_results = len(filtered_games)
        print(num_results)

        # Start building the table HTML with inline CSS styles
        table_html = f"""
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Results | onBoard Games</title>
            <!-- Link to CSS file -->
            <link rel="stylesheet" href="./static/style.css">
            <link rel="icon" href="./static/pics/onboardgames-logo.webp">
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
            <link href="https://fonts.googleapis.com/css2?family=Arima:wght@100..700&family=Roboto:ital,wght@0,100;0,300;0,400;0,500;0,700;0,900;1,100;1,300;1,400;1,500;1,700;1,900&display=swap" rel="stylesheet">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/css/all.min.css" integrity="sha512-Kc323vGBEqzTmouAECnVceyQqyqdsSiqLQISBL29aUW4U/M7pSPA/gEUZQqv1cwx4OnYxTxve5UMg5GT6L4JJg==" crossorigin="anonymous" referrerpolicy="no-referrer" />
        </head>
        <div class="results-container">
        <h2 class="results-heading">Top results for your search</h2>
        """

        # Adicionando o link da loja apenas se existir
        for index, row in filtered_games.iterrows():
            shoplink_html = f"<p><i class='fa-brands fa-amazon'></i> <a href='{row['ShopLink']}' class='shoplink' target='_blank'> Buy on Amazon!</a></p>" if 'ShopLink' in row and pd.notna(row['ShopLink']) else ""
            table_html += f"""
                <div class="game-container">
                <div class="image-name" style="background-image: url('{row['ImagePath']}');">
                    <a href="/game/{index}"><img class="game-image" src='{row['ImagePath']}' width="200" alt='Game Image'></a>
                </div>
                <div class="game-details">
                    <a class="link-game" href="/game/{index}"><h1>{row['Name']}</h1></a>
                    <p><i class="fa-solid fa-weight-scale"></i> Weight: {row['GameWeight']:.1f}</p>
                    <p><i class="fa-solid fa-user"></i> Players: {row.MinPlayers} - {row.MaxPlayers}</p>
                    <p><i class="fa-solid fa-clock"></i> Playtime: {row['ComMaxPlaytime']}</p>            
                    <p><i class="fa-solid fa-ranking-star"></i> Rank: {int(row['Rank:boardgame'])}</p>
                    {shoplink_html}
                </div>
            </div>
            <p class="divider"></p>
            """


        table_html += "<a href='/' class='back'><i class='fa-solid fa-backward-step'></i> Search for another game</a></div>"

        return table_html

    except KeyError:
        return "Invalid difficulty or category selected. Please try again."

@app.route('/game/<int:game_id>')
def game_details(game_id):
    # Retrieve the game details from the DataFrame based on the game_id
    try:
        game = df.iloc[game_id]
        
        # Adicionando o link da loja apenas se existir
        shoplink_html = f"<p class='description'><a href='{game['ShopLink']}' class='shop-link' target='_blank'>Comprar</a></p>" if 'ShopLink' in game and pd.notna(game['ShopLink']) else ""

# Renderizando os detalhes do jogo
        game_html = f"""
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{game['Name']} | onBoard Games</title>
            <link rel="stylesheet" href="../static/style.css">
            <link rel="icon" href="../static/pics/onboardgames-logo.webp">
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
            <link href="https://fonts.googleapis.com/css2?family=Arima:wght@100..700&family=Roboto:ital,wght@0,100;0,300;0,400;0,500;0,700;0,900;1,100;1,300;1,400;1,500;1,700;1,900&display=swap" rel="stylesheet">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/css/all.min.css" integrity="sha512-Kc323vGBEqzTmouAECnVceyQqyqdsSiqLQISBL29aUW4U/M7pSPA/gEUZQqv1cwx4OnYxTxve5UMg5GT6L4JJg==" crossorigin="anonymous" referrerpolicy="no-referrer" />
        </head>
        <div class="game-container">
            <div class="image-name" style="background-image: url('{game['ImagePath']}');">
                <img class="game-image" src='{game['ImagePath']}' width="200" alt='Game Image'>
            </div>
            <div class="game-details">
                <h1>{game['Name']}</h1>
                <p><i class="fa-solid fa-weight-scale"></i> Weight: {game['GameWeight']:.1f}</p>
                <p><i class="fa-solid fa-user"></i> Players: {game.MinPlayers} - {game.MaxPlayers}</p>
                <p><i class="fa-solid fa-clock"></i> Playtime: {game['ComMaxPlaytime']}</p>            
                <p><i class="fa-solid fa-ranking-star"></i> Rank: {int(game['Rank:boardgame'])}</p>
                <p class="description"> {game['Description']}</p>
                <i class="fa-brands fa-amazon"></i> {shoplink_html}
                <button onclick="history.back()" class="back"><i class="fa-solid fa-backward-step"></i> Back to Search Results</button>
            </div>
        </div>
        """
        return game_html
    except IndexError:
        return "Game not found.", 404


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)