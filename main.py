from flask import Flask, request, jsonify, render_template, redirect, url_for
from google.cloud import datastore

app = Flask(__name__)
datastore_client = datastore.Client()

COLLECTION_NAME = "entries"

@app.route("/")
def hello_world():
    query = datastore_client.query(kind='Item')
    items = []
    for entity in query.fetch():
        item = dict(entity)
        item['id'] = entity.key.id
        items.append(item)
    return render_template('MinionHub.html', items = items)

@app.route("/leaderboard")
def hello_world2():
    # Query items from Firestore and order by 'votes' in descending order
    query = datastore_client.query(kind='Item')
    query.order = ['-votes']  # Order by 'votes' in descending order (most to least)

    items = []
    for entity in query.fetch():
        item = dict(entity)
        item['id'] = entity.key.id
        items.append(item)

    return render_template('Leaderboard.html', items=items)

@app.route("/videos")
def hello_world3():
    return render_template('Videos.html',)

@app.route("/liveminions")
def hello_world4():
    return render_template('LiveMinions.html',)

@app.route('/create', methods=['POST'])
def create():
    """Handle form submission to create new item"""
    try:
        name = request.form.get('name')
        votes = request.form.get('votes')

        # Create new entity
        key = datastore_client.key('Item')
        entity = datastore.Entity(key=key)
        entity.update({
            'name': name,
            'votes': votes
        })
        datastore_client.put(entity)

        return redirect(url_for('/'))
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route("/fortnite")
def fortnite():
    return render_template('MinionHub.html')

# Route to render the edit form
@app.route('/edit/<int:entry_id>', methods=['GET'])
def edit_form(entry_id):
    key = datastore_client.key('Item', entry_id)
    entity = datastore_client.get(key)

    if entity:
        entry = dict(entity)
        entry['id'] = entry_id  # Include ID for the form
        return render_template('edit.html', entry=entry)
    else:
        return "Entry not found", 404  # Handle missing entry properly


@app.route('/vote/<int:entry_id>', methods=['POST'])
def vote_entry(entry_id):
    # Fetch the existing entry
    key = datastore_client.key('Item', entry_id)
    entity = datastore_client.get(key)

    if entity:
        # Ensure 'votes' is treated as an integer
        current_votes = entity.get('votes', 0)

        # If 'votes' is stored as a string, we need to cast it to int
        if isinstance(current_votes, str):
            current_votes = int(current_votes)

        entity['votes'] = current_votes + 1  # Increment vote count
        datastore_client.put(entity)  # Save changes to Firestore

        return redirect(url_for('hello_world2'))  # Redirect back to leaderboard
    else:
        return "Entry not found", 404

if __name__ == "__main__":
    app.run(host="127.0.0.1", port = 8080, debug = True)