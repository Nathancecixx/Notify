import os
import json
import sqlite3
import shutil

class Notes_Handler:
    def __init__(self, file_path):
        self.file_path = file_path
        self.conn = sqlite3.connect(self.file_path)
        cursor = self.conn.cursor()
        
        # Create the Notes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create the Tags table to store tags and their ranges
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_id INTEGER,
                tag_name TEXT,
                start_index TEXT,
                end_index TEXT,
                FOREIGN KEY (note_id) REFERENCES Notes(id)
            )
        ''')

        self.conn.commit()

    def save_note(self, title, content, tags):
        cursor = self.conn.cursor()

        # Insert the note into the database, including the HTML content
        cursor.execute('INSERT INTO Notes (title, content) VALUES (?, ?)', (title, content))
        note_id = cursor.lastrowid

        # Insert tags related to the note
        for tag in tags:
            tag_name = tag["tag_name"] 
            start_index = tag["start_index"] 
            end_index = tag["end_index"]
            cursor.execute('INSERT INTO Tags (note_id, tag_name, start_index, end_index) VALUES (?, ?, ?, ?)', 
                           (note_id, tag_name, start_index, end_index))

        self.conn.commit()

    def update_note(self, note_id, title, content, tags):
        cursor = self.conn.cursor()

        # Update the note in the database
        cursor.execute('''
            UPDATE Notes
            SET title = ?, content = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (title, content, note_id))

        # Delete existing tags for this note
        cursor.execute('DELETE FROM Tags WHERE note_id = ?', (note_id,))

        # Insert the new tags related to the note
        for tag in tags:
            tag_name = tag["tag_name"]
            start_index = tag["start_index"]
            end_index = tag["end_index"]
            cursor.execute('INSERT INTO Tags (note_id, tag_name, start_index, end_index) VALUES (?, ?, ?, ?)',
                        (note_id, tag_name, start_index, end_index))

        self.conn.commit()

    def get_note_by_id(self, note_id):
        cursor = self.conn.cursor()

        # Query the note data by ID
        cursor.execute('SELECT * FROM Notes WHERE id = ?', (note_id,))
        note = cursor.fetchone()

        if note:
            # Adjusted indexes based on a typical 5-column schema
            note_data = {
                'id': note[0],
                'title': note[1],
                'content': note[2],
                'created_at': note[3] if len(note) > 3 else None,
                'updated_at': note[4] if len(note) > 4 else None
            }

            # Query the tags related to this note
            cursor.execute('SELECT * FROM Tags WHERE note_id = ?', (note_id,))
            tags = cursor.fetchall()

            # Create a list to store all tag data
            tag_data = []
            for tag in tags:
                tag_data.append({
                    'id': tag[0],
                    'note_id': tag[1],
                    'tag_name': tag[2],
                    'start_index': tag[3],
                    'end_index': tag[4]
                })

            # Return both note and its associated tags
            return note_data, tag_data
        else:
            return None
        
    def fetch_notes(self):
        """Fetch all notes from the database."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, title FROM Notes')
        notes = cursor.fetchall()  # This will return a list of tuples (id, title)
        return notes
