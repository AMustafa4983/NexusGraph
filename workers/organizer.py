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
        print('Organizer Initialized')

    def create_tables(self):
        try:
            # Connect to the PostgreSQL database
            conn = self.conn
            cur = self.cur

            # SQL statements to create tables
            create_tables_sql = """
                CREATE TABLE IF NOT EXISTS papers (
                    paper_id SERIAL PRIMARY KEY,
                    title VARCHAR(255)
                );

                CREATE TABLE IF NOT EXISTS authors (
                    author_id SERIAL PRIMARY KEY,
                    name VARCHAR(255),
                    affiliation_id INT
                );

                CREATE TABLE IF NOT EXISTS affiliations (
                    affiliation_id SERIAL PRIMARY KEY,
                    name VARCHAR(255)
                );

                CREATE TABLE IF NOT EXISTS tags (
                    tag_id SERIAL PRIMARY KEY,
                    description TEXT
                );

                CREATE TABLE IF NOT EXISTS materials (
                    material_id SERIAL PRIMARY KEY,
                    name VARCHAR(255),
                    supplier_id INT
                );

                CREATE TABLE IF NOT EXISTS suppliers (
                    supplier_id SERIAL PRIMARY KEY,
                    name VARCHAR(255),
                    item_specifics TEXT
                );

                CREATE TABLE IF NOT EXISTS methodologies (
                    methodology_id SERIAL PRIMARY KEY,
                    description TEXT
                );

                CREATE TABLE IF NOT EXISTS instructions (
                    instruction_id SERIAL PRIMARY KEY,
                    paper_id INT,
                    methodology_id INT,
                    content TEXT
                );

                CREATE TABLE IF NOT EXISTS experiments (
                    experiment_id SERIAL PRIMARY KEY,
                    title VARCHAR(255),
                    paper_id INT
                );

                CREATE TABLE IF NOT EXISTS experiment_items (
                    experiment_item_id SERIAL PRIMARY KEY,
                    experiment_id INT,
                    material_id INT,
                    usage TEXT
                );

                CREATE TABLE IF NOT EXISTS paper_authors (
                    paper_id INT,
                    author_id INT
                );

                CREATE TABLE IF NOT EXISTS paper_tags (
                    paper_id INT,
                    tag_id INT
                );

                CREATE TABLE IF NOT EXISTS paper_methodologies (
                    paper_id INT,
                    methodology_id INT
                );
            """

            # Execute the SQL statements
            cur.execute(create_tables_sql)

            # Commit the changes and close the connection
            conn.commit()
            cur.close()
            conn.close()

            print("Database tables created successfully.")

        except Exception as e:
            print(f"Error: {e}")
    
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


    def insert_material(self, name, supplier_id):
        # Insert into materials and return material_id
        insert_material_query = "INSERT INTO materials (name, supplier_id) VALUES (%s, %s) RETURNING material_id;"
        self.cur.execute(insert_material_query, (name, supplier_id))
        material_id = self.cur.fetchone()[0]
        self.conn.commit()
        return material_id

    def insert_supplier(self, name, item_specifics):
        # Insert into suppliers and return supplier_id
        insert_supplier_query = "INSERT INTO suppliers (name, item_specifics) VALUES (%s, %s) RETURNING supplier_id;"
        self.cur.execute(insert_supplier_query, (name, item_specifics))
        supplier_id = self.cur.fetchone()[0]
        self.conn.commit()
        return supplier_id

    def link_experiment_material(self, experiment_id, material_id, usage):
        # Link experiment and material
        insert_experiment_material_query = "INSERT INTO experiment_items (experiment_id, material_id, usage) VALUES (%s, %s, %s);"
        self.cur.execute(insert_experiment_material_query, (experiment_id, material_id, usage))
        self.conn.commit()

    def insert_methodology(self, description):
        # Insert into methodologies and return methodology_id
        insert_methodology_query = "INSERT INTO methodologies (description) VALUES (%s) RETURNING methodology_id;"
        self.cur.execute(insert_methodology_query, (description,))
        methodology_id = self.cur.fetchone()[0]
        self.conn.commit()
        return methodology_id

    def link_paper_methodology(self, paper_id, methodology_id):
        # Link paper and methodology
        insert_paper_methodology_query = "INSERT INTO paper_methodologies (paper_id, methodology_id) VALUES (%s, %s);"
        self.cur.execute(insert_paper_methodology_query, (paper_id, methodology_id))
        self.conn.commit()

    def insert_instruction(self, paper_id, methodology_id, content):
        # Insert instruction and link with paper and methodology
        insert_instruction_query = "INSERT INTO instructions (paper_id, methodology_id, content) VALUES (%s, %s, %s);"
        self.cur.execute(insert_instruction_query, (paper_id, methodology_id, content))
        self.conn.commit()

    def insert_experiment(self, title, paper_id):
        # Insert into experiments and return experiment_id
        insert_experiment_query = "INSERT INTO experiments (title, paper_id) VALUES (%s, %s) RETURNING experiment_id;"
        self.cur.execute(insert_experiment_query, (title, paper_id))
        experiment_id = self.cur.fetchone()[0]
        self.conn.commit()
        return experiment_id
    

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

            # Additional logic for other types of data
            if 'instructions' in data:
                for instruction in data['instructions']:
                    methodology_id = self.insert_methodology(instruction['methodology'])
                    paper_id = paper_id  # Assuming you have access to the current paper_id
                    self.link_paper_methodology(paper_id, methodology_id)
                    self.insert_instruction(paper_id, methodology_id, instruction['content'])

            if 'experiments' in data:
                for experiment in data['experiments']:
                    experiment_id = self.insert_experiment(experiment['title'], paper_id)
                    for item in experiment.get('items', []):
                        material_id = self.insert_material(item['material_name'], item['supplier_id'])
                        self.link_experiment_material(experiment_id, material_id, item['usage'])
    