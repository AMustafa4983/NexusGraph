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
-- Dropping and creating the schema
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

-- Papers
CREATE TABLE papers (
    paper_id SERIAL PRIMARY KEY,
    title VARCHAR(255)
);

-- Affiliations
CREATE TABLE affiliations (
    affiliation_id SERIAL PRIMARY KEY,
    name VARCHAR(255)
);

-- Authors
CREATE TABLE authors (
    author_id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    affiliation_id INT,
    FOREIGN KEY (affiliation_id) REFERENCES affiliations(affiliation_id)
);

-- Tags
CREATE TABLE tags (
    tag_id SERIAL PRIMARY KEY,
    description TEXT
);

-- Suppliers
CREATE TABLE suppliers (
    supplier_id SERIAL PRIMARY KEY,
    name VARCHAR(255)
);

-- Materials
CREATE TABLE materials (
    material_id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    supplier_id INT,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
);

-- Methodologies
CREATE TABLE methodologies (
    methodology_id SERIAL PRIMARY KEY,
    description TEXT
);

-- Instructions
CREATE TABLE instructions (
    instruction_id SERIAL PRIMARY KEY,
    paper_id INT,
    methodology_id INT,
    content TEXT,
    FOREIGN KEY (paper_id) REFERENCES papers(paper_id),
    FOREIGN KEY (methodology_id) REFERENCES methodologies(methodology_id)
);

-- Experiments
CREATE TABLE experiments (
    experiment_id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    paper_id INT,
    FOREIGN KEY (paper_id) REFERENCES papers(paper_id)
);

-- Experiment Items
CREATE TABLE experiment_items (
    experiment_item_id SERIAL PRIMARY KEY,
    experiment_id INT,
    material_id INT,
    supplier_id INT,
    usage TEXT,
    FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id),
    FOREIGN KEY (material_id) REFERENCES materials(material_id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
);

-- Junction tables for many-to-many relationships

-- Paper Authors
CREATE TABLE paper_authors (
    paper_id INT,
    author_id INT,
    FOREIGN KEY (paper_id) REFERENCES papers(paper_id),
    FOREIGN KEY (author_id) REFERENCES authors(author_id),
    PRIMARY KEY (paper_id, author_id)
);

-- Paper Tags
CREATE TABLE paper_tags (
    paper_id INT,
    tag_id INT,
    FOREIGN KEY (paper_id) REFERENCES papers(paper_id),
    FOREIGN KEY (tag_id) REFERENCES tags(tag_id),
    PRIMARY KEY (paper_id, tag_id)
);

-- Paper Methodologies
CREATE TABLE paper_methodologies (
    paper_id INT,
    methodology_id INT,
    FOREIGN KEY (paper_id) REFERENCES papers(paper_id),
    FOREIGN KEY (methodology_id) REFERENCES methodologies(methodology_id),
    PRIMARY KEY (paper_id, methodology_id)
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
        insert_paper_query = "INSERT INTO papers (title) VALUES (%s) RETURNING paper_id;"
        self.cur.execute(insert_paper_query, (title,))
        paper_id = self.cur.fetchone()[0]
        self.conn.commit()

        for tag in tags:
            self.insert_tag(paper_id, tag)
        return paper_id
    
    def insert_author(self, name, affiliation):
        insert_author_query = "INSERT INTO authors (name) VALUES (%s) RETURNING author_id;"
        self.cur.execute(insert_author_query, (name,))
        author_id = self.cur.fetchone()[0]

        self.cur.execute("SELECT affiliation_id FROM affiliations WHERE name = %s;", (affiliation,))
        affiliation_result = self.cur.fetchone()
        if affiliation_result:
            affiliation_id = affiliation_result[0]
        else:
            insert_affiliation_query = "INSERT INTO affiliations (name) VALUES (%s) RETURNING affiliation_id;"
            self.cur.execute(insert_affiliation_query, (affiliation,))
            affiliation_id = self.cur.fetchone()[0]

        update_author_query = "UPDATE authors SET affiliation_id = %s WHERE author_id = %s;"
        self.cur.execute(update_author_query, (affiliation_id, author_id))

        self.conn.commit()
        return author_id
    
    def link_paper_author(self, paper_id, author_id):
        insert_paper_author_query = "INSERT INTO paper_authors (paper_id, author_id) VALUES (%s, %s);"
        self.cur.execute(insert_paper_author_query, (paper_id, author_id))
        self.conn.commit()


    def insert_tag(self, paper_id, tag_description):
        self.cur.execute("SELECT tag_id FROM tags WHERE description = %s;", (tag_description,))
        tag_result = self.cur.fetchone()
        if tag_result:
            tag_id = tag_result[0]
        else:
            insert_tag_query = "INSERT INTO tags (description) VALUES (%s) RETURNING tag_id;"
            self.cur.execute(insert_tag_query, (tag_description,))
            tag_id = self.cur.fetchone()[0]
            self.conn.commit()

        link_tag_query = "INSERT INTO paper_tags (paper_id, tag_id) VALUES (%s, %s);"
        self.cur.execute(link_tag_query, (paper_id, tag_id))
        self.conn.commit()



    def insert_material(self, name):
        insert_material_query = "INSERT INTO materials (name) VALUES (%s) RETURNING material_id;"
        self.cur.execute(insert_material_query, (name,))
        material_id = self.cur.fetchone()[0]
        self.conn.commit()
        return material_id

    def insert_supplier(self, name):
        insert_supplier_query = "INSERT INTO suppliers (name) VALUES (%s) RETURNING supplier_id;"
        self.cur.execute(insert_supplier_query, (name,))
        supplier_id = self.cur.fetchone()[0]
        self.conn.commit()
        return supplier_id


    def link_experiment_material(self, experiment_id, material_id, supplier_id, usage):
        insert_experiment_material_query = "INSERT INTO experiment_items (experiment_id, material_id, supplier_id, usage) VALUES (%s, %s, %s, %s);"
        self.cur.execute(insert_experiment_material_query, (experiment_id, material_id, supplier_id, usage))
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
            # Process papers and their related data
            if 'title' in data:
                paper_id = self.insert_paper(data['title'], data.get('tags', []))

                # Process authors for the paper
                for author in data.get('authors', []):
                    author_id = self.insert_author(author['name'], author['affiliation'])
                    self.link_paper_author(paper_id, author_id)

                # Process instructions and methodologies
                for instruction in data.get('instructions', []):
                    # Check if methodology exists or is new
                    methodology_description = instruction.get('methodology')
                    if methodology_description:
                        methodology_id = self.insert_methodology(methodology_description)
                        self.link_paper_methodology(paper_id, methodology_id)
                        self.insert_instruction(paper_id, methodology_id, instruction['content'])

                # Process experiments
                for experiment in data.get('experiments', []):
                    experiment_id = self.insert_experiment(experiment['experiment_title'], paper_id)

                    # Process experiment items
                    for item in experiment.get('experiment_items', []):
                        material_name = item.get('material')
                        supplier_name = item.get('supplier')
                        material_usage = item.get('material_usage', '')

                        # Check if material and supplier exist or are new
                        if material_name:
                            material_id = self.insert_material(material_name)
                        else:
                            material_id = None  # Handle cases where material is not specified

                        if supplier_name:
                            supplier_id = self.insert_supplier(supplier_name)
                        else:
                            supplier_id = None  # Handle cases where supplier is not specified

                        if material_id is not None:
                            self.link_experiment_material(experiment_id, material_id, supplier_id, material_usage)
