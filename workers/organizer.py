import traceback
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session

DATABASE_URL = "postgresql://postgres:ilfgbkOKhLwQhCQNttQZpBDzmrrRAwVx@roundhouse.proxy.rlwy.net:36038/railway"

# Create an engine with a connection pool
engine = create_engine(
    DATABASE_URL,
    pool_size=20,          # The size of the pool to be maintained
    max_overflow=10,       # The maximum overflow size
    pool_timeout=30,       # The maximum time to wait for a connection
    pool_recycle=1800,     # Time to recycle connections (in seconds)
    pool_pre_ping=True     # Test connections for liveness
)

SessionFactory = sessionmaker(bind=engine)
Session = scoped_session(SessionFactory)

class Organizer:
    def __init__(self):
        self.session = Session()

    def clear_database(self):
        try:
            # Order of deletion is important to avoid foreign key constraint violations
            tables = [
                'experiment_items', 'instructions', 'experiments',
                'paper_tags', 'paper_methodologies', 'paper_authors',
                'methodologies', 'materials', 'suppliers',
                'tags', 'authors', 'affiliations', 'papers'
            ]
            for table in tables:
                self.session.execute(text(f"DELETE FROM {table};"))
            self.session.commit()
            print("Database cleared successfully.")
        except Exception as e:
            self.session.rollback()
            print(f"Error: {e}")
            traceback.print_exc()


    def create_tables(self):
        try:
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

            -- Experiments
            CREATE TABLE experiments (
                experiment_id SERIAL PRIMARY KEY,
                title VARCHAR(255),
                paper_id INT,
                FOREIGN KEY (paper_id) REFERENCES papers(paper_id)
            );

            -- Instructions
            CREATE TABLE instructions (
                instruction_id SERIAL PRIMARY KEY,
                experiment_id INT,
                methodology_id INT,
                content TEXT,
                FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id),
                FOREIGN KEY (methodology_id) REFERENCES methodologies(methodology_id)
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
            self.session.execute(text(create_tables_sql))
            self.session.commit()
            print("Database tables created successfully.")
        except Exception as e:
            self.session.rollback()
            print(f"Error: {e}")
            traceback.print_exc()

 
    def insert_paper(self, title, tags):
        try:
            insert_paper_query = text("INSERT INTO papers (title) VALUES (:title) RETURNING paper_id;")
            result = self.session.execute(insert_paper_query, {'title': title})
            paper_id = result.fetchone()[0]
            self.session.commit()

            for tag in tags:
                self.insert_tag(paper_id, tag)

            print(f"Inserted paper with ID: {paper_id}")
            return paper_id
        except Exception as e:
            self.session.rollback()
            print(f"Error inserting paper: {e}")
            traceback.print_exc()
            return None

    def insert_author(self, name, affiliation, paper_id):
        try:
            insert_author_query = text("INSERT INTO authors (name) VALUES (:name) RETURNING author_id;")
            result = self.session.execute(insert_author_query, {'name': name})
            author_id = result.fetchone()[0]
            self.session.commit()

            insert_affiliation_query = text("INSERT INTO affiliations (name) VALUES (:name) RETURNING affiliation_id;")
            result = self.session.execute(insert_affiliation_query, {'name': affiliation})
            affiliation_id = result.fetchone()[0]
            self.session.commit()

            update_author_query = text("UPDATE authors SET affiliation_id = :affiliation_id WHERE author_id = :author_id;")
            self.session.execute(update_author_query, {'affiliation_id': affiliation_id, 'author_id': author_id})
            self.session.commit()

            self.link_paper_author(paper_id, author_id)
            print(f"Inserted author with ID: {author_id} and linked to paper ID: {paper_id}")
            return author_id
        except Exception as e:
            self.session.rollback()
            print(f"Error inserting author: {e}")
            traceback.print_exc()
            return None

    def link_paper_author(self, paper_id, author_id):
        try:
            link_paper_author_query = text("INSERT INTO paper_authors (paper_id, author_id) VALUES (:paper_id, :author_id);")
            self.session.execute(link_paper_author_query, {'paper_id': paper_id, 'author_id': author_id})
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            print(f"Error linking paper and author: {e}")
            traceback.print_exc()

    def insert_tag(self, paper_id, tag_description):
        try:
            tag_query = text("SELECT tag_id FROM tags WHERE description = :description;")
            tag_result = self.session.execute(tag_query, {'description': tag_description}).fetchone()

            if tag_result:
                tag_id = tag_result[0]
            else:
                insert_tag_query = text("INSERT INTO tags (description) VALUES (:description) RETURNING tag_id;")
                result = self.session.execute(insert_tag_query, {'description': tag_description})
                tag_id = result.fetchone()[0]
                self.session.commit()

            link_tag_query = text("INSERT INTO paper_tags (paper_id, tag_id) VALUES (:paper_id, :tag_id);")
            self.session.execute(link_tag_query, {'paper_id': paper_id, 'tag_id': tag_id})
            self.session.commit()
            print(f"Inserted tag '{tag_description}' and linked to paper ID: {paper_id}")
        except Exception as e:
            self.session.rollback()
            print(f"Error inserting tag: {e}")
            traceback.print_exc()

    def insert_material(self, name):
        try:
            insert_material_query = text("INSERT INTO materials (name) VALUES (:name) RETURNING material_id;")
            result = self.session.execute(insert_material_query, {'name': name})
            material_id = result.fetchone()[0]
            self.session.commit()
            print(f"Inserted material with ID: {material_id}")
            return material_id
        except Exception as e:
            self.session.rollback()
            print(f"Error inserting material: {e}")
            traceback.print_exc()
            return None

    def insert_supplier(self, name):
        try:
            insert_supplier_query = text("INSERT INTO suppliers (name) VALUES (:name) RETURNING supplier_id;")
            result = self.session.execute(insert_supplier_query, {'name': name})
            supplier_id = result.fetchone()[0]
            self.session.commit()
            print(f"Inserted supplier with ID: {supplier_id}")
            return supplier_id
        except Exception as e:
            self.session.rollback()
            print(f"Error inserting supplier: {e}")
            traceback.print_exc()
            return None

    def insert_methodology_and_instructions(self, experiment_id, methodologies, instructions):
        try:
            for methodology in methodologies:
                print(f"Inserting methodology: {methodology}")
                insert_methodology_query = text("INSERT INTO methodologies (description) VALUES (:description) RETURNING methodology_id;")
                result = self.session.execute(insert_methodology_query, {'description': methodology})
                methodology_id = result.fetchone()[0]
                self.session.commit()
                print(f"Inserted methodology with ID: {methodology_id}")

                for instruction in instructions:
                    print(f"Inserting instruction for methodology ID: {methodology_id}, content: {instruction}")
                    insert_instruction_query = text("INSERT INTO instructions (experiment_id, methodology_id, content) VALUES (:experiment_id, :methodology_id, :content);")
                    self.session.execute(insert_instruction_query, {'experiment_id': experiment_id, 'methodology_id': methodology_id, 'content': instruction})
                    self.session.commit()
                    print(f"Inserted instruction with content: {instruction}")
        except Exception as e:
            self.session.rollback()
            print(f"Error inserting methodology and instructions: {e}")
            traceback.print_exc()

    def insert_experiment(self, title, paper_id, experiment_items):
        try:
            insert_experiment_query = text("INSERT INTO experiments (title, paper_id) VALUES (:title, :paper_id) RETURNING experiment_id;")
            result = self.session.execute(insert_experiment_query, {'title': title, 'paper_id': paper_id})
            experiment_id = result.fetchone()[0]
            self.session.commit()
            print(f"Inserted experiment with ID: {experiment_id}")

            for item in experiment_items:
                material_id = self.insert_material(item['material'])
                supplier_id = self.insert_supplier(item['supplier'])
                self.link_experiment_material(experiment_id, material_id, supplier_id, item['material_usage'])

            return experiment_id
        except Exception as e:
            self.session.rollback()
            print(f"Error inserting experiment: {e}")
            traceback.print_exc()
            return None

    def link_experiment_material(self, experiment_id, material_id, supplier_id, usage):
        try:
            link_experiment_material_query = text("INSERT INTO experiment_items (experiment_id, material_id, supplier_id, usage) VALUES (:experiment_id, :material_id, :supplier_id, :usage);")
            self.session.execute(link_experiment_material_query, {'experiment_id': experiment_id, 'material_id': material_id, 'supplier_id': supplier_id, 'usage': usage})
            self.session.commit()
            print(f"Linked material ID: {material_id} and supplier ID: {supplier_id} to experiment ID: {experiment_id} with usage: {usage}")
        except Exception as e:
            self.session.rollback()
            print(f"Error linking experiment and material: {e}")
            traceback.print_exc()

    def close(self):
        self.session.close()

    def process_json(self, json_data):
        paper_id = None
        try:
            for data in json_data:
                if 'title' in data:
                    print(f"Inserting paper with title: {data['title']}")
                    paper_id = self.insert_paper(data['title'], data.get('tags', []))
                    print(f"Inserted paper with ID: {paper_id}")

                    for author in data.get('authors', []):
                        print(f"Inserting author: {author['name']}, Affiliation: {author['affiliation']}")
                        self.insert_author(author['name'], author['affiliation'], paper_id)
                        print(f"Inserted author: {author['name']}")

                if 'experiments' in data:
                    for experiment in data['experiments']:
                        print(f"Inserting experiment with title: {experiment['experiment_title']}")
                        experiment_id = self.insert_experiment(experiment['experiment_title'], paper_id, experiment.get('experiment_items', []))
                        print(f"Inserted experiment with ID: {experiment_id}")
                        
                        # Insert methodologies and instructions for this experiment
                        if 'methodologies' in experiment or 'instructions' in experiment:
                            print(f"Inserting methodologies and instructions for experiment ID: {experiment_id}")
                            self.insert_methodology_and_instructions(experiment_id, experiment.get('methodologies', []), experiment.get('instructions', []))
                            print(f"Inserted methodologies and instructions for experiment ID: {experiment_id}")

            print("Organizer saved information in the database successfully!")

        except Exception as e:
            print(f"Error processing JSON data: {e}")
            traceback.print_exc()

    def get_all_papers(self):
        try:
            select_papers_query = text("""
            SELECT p.paper_id, p.title, string_agg(DISTINCT a.name, ', ') AS authors, string_agg(DISTINCT t.description, ', ') AS tags
            FROM papers p
            LEFT JOIN paper_authors pa ON p.paper_id = pa.paper_id
            LEFT JOIN authors a ON pa.author_id = a.author_id
            LEFT JOIN paper_tags pt ON p.paper_id = pt.paper_id
            LEFT JOIN tags t ON pt.tag_id = t.tag_id
            GROUP BY p.paper_id, p.title;
            """)
            result = self.session.execute(select_papers_query)
            papers = []
            for row in result.fetchall():
                paper_id, title, author, tag = row
                paper = {'id': paper_id, 'title': title}
                if author:
                    paper['authors'] = author.split(", ")
                if tag:
                    paper['tags'] = tag.split(", ")
                papers.append(paper)
            return papers
        except Exception as e:
            print(f"Error: {e}")
            traceback.print_exc()
            return None

    def get_paper_details(self, paper_id):
        try:
            select_paper_query = text("""
                SELECT 
                    p.title, 
                    STRING_AGG(DISTINCT a.name, ', ') AS authors,
                    STRING_AGG(DISTINCT t.description, ', ') AS tags,
                    e.experiment_id,
                    e.title AS experiment_title,
                    m.name AS material,
                    s.name AS supplier,
                    ei.usage AS material_usage,
                    meth.description AS methodology,
                    i.content AS instruction
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
                    instructions i ON e.experiment_id = i.experiment_id
                LEFT JOIN 
                    methodologies meth ON i.methodology_id = meth.methodology_id
                WHERE 
                    p.paper_id = :paper_id
                GROUP BY 
                    p.title, e.experiment_id, e.title, m.name, s.name, ei.usage, meth.description, i.content;
            """)
            
            result = self.session.execute(select_paper_query, {'paper_id': paper_id})
            paper_details = {}
            experiments_map = {}
            for row in result.fetchall():
                title, authors, tags, experiment_id, experiment_title, material, supplier, material_usage, methodology, instruction = row
                if not paper_details:
                    paper_details = {
                        'title': title,
                        'authors': authors.split(', ') if authors else [],
                        'tags': tags.split(', ') if tags else [],
                        'experiments': []
                    }
                if experiment_id not in experiments_map:
                    experiment = {
                        'experiment_id': experiment_id,
                        'experiment_title': experiment_title,
                        'experiment_items': set(),
                        'methodologies': set(),
                        'instructions': set()
                    }
                    experiments_map[experiment_id] = experiment
                    paper_details['experiments'].append(experiment)
                
                experiments_map[experiment_id]['experiment_items'].add((material, supplier, material_usage))
                if methodology:
                    experiments_map[experiment_id]['methodologies'].add(methodology)
                if instruction:
                    experiments_map[experiment_id]['instructions'].add(instruction)
            
            # Convert sets to lists and structure experiment items properly
            for experiment in paper_details['experiments']:
                experiment['experiment_items'] = [
                    {'material': item[0], 'supplier': item[1], 'material_usage': item[2]}
                for item in experiment['experiment_items']]
                experiment['methodologies'] = list(experiment['methodologies'])
                experiment['instructions'] = list(experiment['instructions'])

            # Debugging statements to check the final structure
            print("Debug: Final paper_details structure:", paper_details)
                    
            return paper_details
        except Exception as e:
            print(f"Error: {e}")
            traceback.print_exc()
            return None
