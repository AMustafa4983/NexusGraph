import psycopg2

class Organizer:
    def __init__(self, dbname, user, password, host='localhost', port='5432'):
        self.conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.cur = self.conn.cursor()
        print('Organiezer Initialized')
    
    def insert_paper(self, title, tags):
        # Insert into papers and return paper_id
        insert_paper_query = "INSERT INTO papers (title) VALUES (%s) RETURNING paper_id;"
        self.cur.execute(insert_paper_query, (title,))
        paper_id = self.cur.fetchone()[0]
        self.conn.commit()

        # Insert tags if provided
        for tag in tags:
            self.insert_tag(paper_id, tag)
        return paper_id

    def insert_author(self, name, affiliation):
        # Insert into authors and return author_id
        insert_author_query = "INSERT INTO authors (name, affiliation_id) VALUES (%s, %s) RETURNING author_id;"
        self.cur.execute(insert_author_query, (name, affiliation))
        author_id = self.cur.fetchone()[0]
        self.conn.commit()
        return author_id

    def link_paper_author(self, paper_id, author_id):
        # Link paper and author
        insert_paper_author_query = "INSERT INTO paper_authors (paper_id, author_id) VALUES (%s, %s);"
        self.cur.execute(insert_paper_author_query, (paper_id, author_id))
        self.conn.commit()

    def insert_tag(self, paper_id, tag_description):
        # Insert tag and link with paper
        insert_tag_query = "INSERT INTO tags (description) VALUES (%s) RETURNING tag_id;"
        self.cur.execute(insert_tag_query, (tag_description,))
        tag_id = self.cur.fetchone()[0]
        self.conn.commit()

        link_tag_query = "INSERT INTO paper_tags (paper_id, tag_id) VALUES (%s, %s);"
        self.cur.execute(link_tag_query, (paper_id, tag_id))
        self.conn.commit()

    

    def close(self):
        self.cur.close()
        self.conn.close()

    def process_json(self, json_data):
        # Assuming json_data is a list of dictionaries
        for data in json_data:
            if 'title' in data:
                paper_id = self.insert_paper(data['title'], data.get('tags', []))
                for author in data.get('authors', []):
                    author_id = self.insert_author(author['name'], author['affiliation'])
                    self.link_paper_author(paper_id, author_id)

            # Additional logic for other types of data (instructions, experiments, etc.)

    