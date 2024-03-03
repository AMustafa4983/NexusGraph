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

    def clear_database(self):
        try:
            # Connect to the PostgreSQL database
            conn = self.conn
            cur = self.cur

            # SQL statements to clear all tables
            tables = [
                'paper_tags', 'paper_methodologies', 'paper_authors',
                'experiment_items', 'experiments', 'instructions',
                'methodologies', 'materials', 'suppliers',
                'tags', 'authors', 'affiliations', 'papers'
            ]

            for table in tables:
                cur.execute(f"DELETE FROM {table};")

            # Commit the changes and close the connection
            conn.commit()
            cur.close()
            conn.close()

            print("Database cleared successfully.")

        except Exception as e:
            print(f"Error: {e}")
    
    
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
        # Insert paper and get paper_id
        insert_paper_query = "INSERT INTO papers (title) VALUES (%s) RETURNING paper_id;"
        self.cur.execute(insert_paper_query, (title,))
        paper_id = self.cur.fetchone()[0]
        self.conn.commit()

        # Insert tags
        for tag in tags:
            self.insert_tag(paper_id, tag)

        return paper_id
    
    def insert_author(self, name, affiliation, paper_id):
        # Insert author and get author_id
        insert_author_query = "INSERT INTO authors (name) VALUES (%s) RETURNING author_id;"
        self.cur.execute(insert_author_query, (name,))
        author_id = self.cur.fetchone()[0]
        self.conn.commit()

        # Insert affiliation
        insert_affiliation_query = "INSERT INTO affiliations (name) VALUES (%s) RETURNING affiliation_id;"
        self.cur.execute(insert_affiliation_query, (affiliation,))
        affiliation_id = self.cur.fetchone()[0]
        self.conn.commit()

        # Link author with affiliation
        update_author_query = "UPDATE authors SET affiliation_id = %s WHERE author_id = %s;"
        self.cur.execute(update_author_query, (affiliation_id, author_id))
        self.conn.commit()

        # Link paper and author
        self.link_paper_author(paper_id, author_id)

        return author_id

    def link_paper_author(self, paper_id, author_id):
        # Link paper and author
        link_paper_author_query = "INSERT INTO paper_authors (paper_id, author_id) VALUES (%s, %s);"
        self.cur.execute(link_paper_author_query, (paper_id, author_id))
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


    def insert_methodology_and_instructions(self, paper_id, methodologies, instructions):
        for methodology in methodologies:
            # Insert methodology and get methodology_id
            insert_methodology_query = "INSERT INTO methodologies (description) VALUES (%s) RETURNING methodology_id;"
            self.cur.execute(insert_methodology_query, (methodology,))
            methodology_id = self.cur.fetchone()[0]
            self.conn.commit()

            # Link paper and methodology
            self.link_paper_methodology(paper_id, methodology_id)

        for instruction in instructions:
            # Insert instruction
            insert_instruction_query = "INSERT INTO instructions (paper_id, methodology_id, content) VALUES (%s, %s, %s);"
            self.cur.execute(insert_instruction_query, (paper_id, methodology_id, instruction))
            self.conn.commit()
    
    def link_paper_methodology(self, paper_id, methodology_id):
        # Link paper and methodology
        link_paper_methodology_query = "INSERT INTO paper_methodologies (paper_id, methodology_id) VALUES (%s, %s);"
        self.cur.execute(link_paper_methodology_query, (paper_id, methodology_id))
        self.conn.commit()


    def insert_instruction(self, paper_id, methodology_id, content):
        # Insert instruction and link with paper and methodology
        insert_instruction_query = "INSERT INTO instructions (paper_id, methodology_id, content) VALUES (%s, %s, %s);"
        self.cur.execute(insert_instruction_query, (paper_id, methodology_id, content))
        self.conn.commit()

    def insert_experiment(self, title, paper_id, experiment_items):
        # Insert experiment and get experiment_id
        insert_experiment_query = "INSERT INTO experiments (title, paper_id) VALUES (%s, %s) RETURNING experiment_id;"
        self.cur.execute(insert_experiment_query, (title, paper_id))
        experiment_id = self.cur.fetchone()[0]
        self.conn.commit()

        # Process experiment items
        for item in experiment_items:
            material_id = self.insert_material(item['material'])
            supplier_id = self.insert_supplier(item['supplier'])
            self.link_experiment_material(experiment_id, material_id, supplier_id, item['material_usage'])

        return experiment_id

    def link_experiment_material(self, experiment_id, material_id, supplier_id, usage):
        # Link experiment and material
        link_experiment_material_query = "INSERT INTO experiment_items (experiment_id, material_id, supplier_id, usage) VALUES (%s, %s, %s, %s);"
        self.cur.execute(link_experiment_material_query, (experiment_id, material_id, supplier_id, usage))
        self.conn.commit()


    def close(self):
        self.cur.close()
        self.conn.close()

    
    def process_json(self, json_data):
        paper_id = None

        for data in json_data:
            if 'title' in data:
                paper_id = self.insert_paper(data['title'], data.get('tags', []))
                for author in data.get('authors', []):
                    self.insert_author(author['name'], author['affiliation'], paper_id)

            if 'experiments' in data and paper_id:
                for experiment in data['experiments']:
                    self.insert_experiment(experiment['experiment_title'], paper_id, experiment.get('experiment_items', []))

            if 'instructions' in data and paper_id:
                self.insert_methodology_and_instructions(paper_id, data.get('methodologies', []), data.get('instructions', []))

    def get_all_papers(self):
        try:
            select_papers_query = """
SELECT p.paper_id, p.title, string_agg(DISTINCT a.name, ', ') AS authors, string_agg(DISTINCT t.description, ', ') AS tags
FROM papers p
LEFT JOIN paper_authors pa ON p.paper_id = pa.paper_id
LEFT JOIN authors a ON pa.author_id = a.author_id
LEFT JOIN paper_tags pt ON p.paper_id = pt.paper_id
LEFT JOIN tags t ON pt.tag_id = t.tag_id
GROUP BY p.paper_id, p.title;

            """
            self.cur.execute(select_papers_query)
            papers = {}
            for row in self.cur.fetchall():
                paper_id, title, author, tag = row
                if paper_id not in papers:
                    papers[paper_id] = {'title': title, 'authors': [], 'tags': []}
                if author:
                    papers[paper_id]['authors'].append(author)
                if tag:
                    papers[paper_id]['tags'].append(tag)
            return papers
        except Exception as e:
            print(f"Error: {e}")



    def get_paper_details(self, paper_id):
        try:
            select_paper_query = """
                SELECT 
    p.title, 
    STRING_AGG(DISTINCT a.name, ', ') AS authors,
    STRING_AGG(DISTINCT t.description, ', ') AS tags,
    STRING_AGG(DISTINCT e.title, ', ') AS experiment_titles,
    STRING_AGG(DISTINCT m.name, ', ') AS materials,
    STRING_AGG(DISTINCT s.name, ', ') AS suppliers,
    STRING_AGG(DISTINCT ei.usage, ', ') AS material_usages,
    STRING_AGG(DISTINCT meth.description, ', ') AS methodologies,
    STRING_AGG(DISTINCT i.content, ', ') AS instructions
FROM 
    papers p
LEFT JOIN 
    paper_authors pa ON p.paper_id = pa.paper_id
LEFT JOIN 
    authors a ON pa.author_id = a.author_id
LEFT JOIN 
    paper_tags pt ON p.paper_id = pt.paper_id
LEFT JOIN 
    tags t ON pt.tag_id = t.tag_id
LEFT JOIN 
    experiments e ON p.paper_id = e.paper_id
LEFT JOIN 
    experiment_items ei ON e.experiment_id = ei.experiment_id
LEFT JOIN 
    materials m ON ei.material_id = m.material_id
LEFT JOIN 
    suppliers s ON ei.supplier_id = s.supplier_id
LEFT JOIN 
    instructions i ON p.paper_id = i.paper_id
LEFT JOIN 
    methodologies meth ON i.methodology_id = meth.methodology_id
WHERE 
    p.paper_id = %s
GROUP BY 
    p.title;

            """
            self.cur.execute(select_paper_query, (paper_id,))
            paper_details = {}
            for row in self.cur.fetchall():
                title, authors, tags, experiment_title, material, supplier, material_usage, methodology, instruction = row
                if not paper_details:
                    paper_details = {
                        'title': title,
                        'authors': authors.split(',') if authors else [],
                        'tags': tags.split(',') if tags else [],
                        'experiments': [],
                        'methodologies': [],
                        'materials': [],
                        'suppliers': [],
                        'instructions': []
                    }
                if experiment_title:
                    paper_details['experiments'].append({
                        'experiment_title': experiment_title,
                        'experiment_items': [{'material': material, 'supplier': supplier, 'material_usage': material_usage}]
                    })
                if methodology:
                    paper_details['methodologies'].append(methodology)
                if instruction:
                    paper_details['instructions'].append(instruction)
            return paper_details
        except Exception as e:
            print(f"Error: {e}")
