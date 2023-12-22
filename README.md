# NexusGraph Readme

NexusGraph is a powerful tool designed to assist researchers in accessing and organizing a vast array of open-source academic papers. This readme file provides an overview of NexusGraph's capabilities, its database schema, and key information for users and developers.

## Introduction

NexusGraph offers the following features:

- **Title-based Categorization:** The tool categorizes papers based on their titles, making it easier to search for specific topics.

- **Author Indexing:** NexusGraph lists all authors for each paper along with their academic affiliations, facilitating author-focused research.

- **Materials Cataloging:** It details all materials used in the studies, which is essential for experimental replication and methodological understanding.

- **Supplier and Item Specifics:** NexusGraph provides comprehensive information on each material, including supplier details and its purpose in the research, aiding in resource procurement.

- **Methodological Breakdown:** The tool breaks down the instructions or methodologies used in the studies, enhancing the user's ability to grasp and apply the research techniques.

## Database Schema

### 1. papers
- **Description:** Stores information about academic papers.
- **Fields:**
  - `paper_id`: A unique identifier for each paper (auto-incrementing integer, primary key).
  - `title`: The title of the academic paper (variable character string).

### 2. authors
- **Description:** Contains detailed information about authors of the papers.
- **Fields:**
  - `author_id`: A unique identifier for each author (auto-incrementing integer, primary key).
  - `name`: The name of the author (variable character string).
  - `affiliation_id`: A foreign key referencing the affiliation_id in the affiliations table (institution or organization affiliation).

### 3. affiliations
- **Description:** Lists the various academic or research affiliations.
- **Fields:**
  - `affiliation_id`: A unique identifier for each affiliation (auto-incrementing integer, primary key).
  - `name`: The name of the institution or organization (variable character string).

### 4. tags
- **Description:** Categorizes papers into different thematic areas or keywords.
- **Fields:**
  - `tag_id`: A unique identifier for each tag (auto-incrementing integer, primary key).
  - `Description`: A description or name of the tag (text).

### 5. materials
- **Description:** Details the materials used in the research studies.
- **Fields:**
  - `material_id`: A unique identifier for each material (auto-incrementing integer, primary key).
  - `name`: The name of the material (variable character string).
  - `supplier_id`: A foreign key linking to the suppliers table (identifying the supplier of the material).

### 6. suppliers
- **Description:** Contains information about suppliers of various materials.
- **Fields:**
  - `supplier_id`: A unique identifier for each supplier (auto-incrementing integer, primary key).
  - `name`: The name of the supplier (variable character string).
  - `item_specifics`: Specific details or descriptions of the items supplied (text).

### 7. methodologies
- **Description:** Describes the different methodologies used in the research papers.
- **Fields:**
  - `methodology_id`: A unique identifier for each methodology (auto-incrementing integer, primary key).
  - `Description`: A detailed description of the research methodology (text).

### 8. instructions
- **Description:** Provides specific instructions or methodologies used in the studies.
- **Fields:**
  - `instruction_id`: A unique identifier for each set of instructions (auto-incrementing integer, primary key).
  - `paper_id`: A foreign key referencing the paper_id in the papers table.
  - `methodology_id`: A foreign key referencing the methodology_id in the methodologies table.
  - `content`: The textual content of the instructions (text).

### 9. experiments
- **Description:** Records the different experiments conducted within the research studies.
- **Fields:**
  - `experiment_id`: A unique identifier for each experiment (auto-incrementing integer, primary key).
  - `title`: The title or name of the experiment (variable character string).
  - `paper_id`: A foreign key linking to the papers table (indicating the paper associated with the experiment).

### 10. experiment_items
- **Description:** Details about items or materials used in each experiment.
- **Fields:**
  - `experiment_item_id`: A unique identifier for each experiment item (auto-incrementing integer, primary key).
  - `experiment_id`: A foreign key linking to the experiments table.
  - `material_id`: A foreign key linking to the materials table (identifying the material used).
  - `Usage`: Description of how the material is used in the experiment (text).

## Junction Tables for Many-to-Many Relationships

These tables manage the many-to-many relationships between various entities:

### paper_authors
- **Description:** Links papers to their respective authors.
- **Fields:**
  - `paper_id`: A foreign key referencing the papers table.
  - `author_id`: A foreign key referencing the authors table.

### paper_tags
- **Description:** Associates papers with multiple tags.
- **Fields:**
  - `paper_id`: A foreign key referencing the papers table.
  - `tag_id`: A foreign key referencing the tags table.

### paper_methodologies
- **Description:** Connect papers to various methodologies used in them.
- **Fields:**
  - `paper_id`: A foreign key referencing the papers table.
  - `methodology_id`: A foreign key referencing the methodologies table.

## Conclusion

NexusGraph is a versatile tool for researchers, enabling efficient organization and access to academic papers. Developers can utilize the provided schema to build applications that leverage its rich features. For further information or inquiries, please feel free to engage in a dialogue or ask questions.
