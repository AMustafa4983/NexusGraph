# NexusGraph Readme

NexusGraph is a powerful tool designed to assist researchers in accessing and organizing a vast array of open-source academic papers. This readme file provides an overview of NexusGraph's capabilities, its database schema, and key information for users and developers.

## Introduction

NexusGraph offers the following features:

- **Title-based Categorization:** The tool categorizes papers based on their titles, making it easier to search for specific topics.

- **Author Indexing:** NexusGraph lists all authors for each paper along with their academic affiliations, facilitating author-focused research.

- **Materials Cataloging:** It details all materials used in the studies, which is essential for experimental replication and methodological understanding.

- **Supplier and Item Specifics:** NexusGraph provides comprehensive information on each material, including supplier details and its purpose in the research, aiding in resource procurement.

- **Methodological Breakdown:** The tool breaks down the instructions or methodologies used in the studies, enhancing the user's ability to grasp and apply the research techniques.

Certainly! Below is a description of each database table you can include in your GitHub README file. This description will help users understand the structure and purpose of each table in your database.

---

## Database Tables Description

### `papers`

This table stores information about research papers.

- **paper_id**: A unique identifier for each paper (Primary Key).
- **title**: The title of the research paper.

### `affiliations`

This table holds details about the affiliations of authors.

- **affiliation_id**: A unique identifier for each affiliation (Primary Key).
- **name**: The name of the affiliation, such as a university or research institution.

### `authors`

This table contains information about the authors of the papers.

- **author_id**: A unique identifier for each author (Primary Key).
- **name**: The name of the author.
- **affiliation_id**: The identifier for the author's affiliation, linking to the `affiliations` table (Foreign Key).

### `tags`

This table is used to store tags related to the papers.

- **tag_id**: A unique identifier for each tag (Primary Key).
- **description**: A description or name of the tag.

### `suppliers`

This table keeps track of suppliers for various materials used in experiments.

- **supplier_id**: A unique identifier for each supplier (Primary Key).
- **name**: The name of the supplier.

### `materials`

This table lists materials used in the experiments.

- **material_id**: A unique identifier for each material (Primary Key).
- **name**: The name of the material.
- **supplier_id**: The identifier for the supplier of the material, linking to the `suppliers` table (Foreign Key).

### `methodologies`

This table records different methodologies used in the research.

- **methodology_id**: A unique identifier for each methodology (Primary Key).
- **description**: A detailed description of the methodology.

### `instructions`

This table includes instructions or procedures followed in the research.

- **instruction_id**: A unique identifier for each instruction (Primary Key).
- **paper_id**: The identifier of the paper these instructions relate to, linking to the `papers` table (Foreign Key).
- **methodology_id**: The identifier of the methodology used, linking to the `methodologies` table (Foreign Key).
- **content**: The detailed content of the instruction.

### `experiments`

This table stores information about experiments conducted in the research.

- **experiment_id**: A unique identifier for each experiment (Primary Key).
- **title**: The title or name of the experiment.
- **paper_id**: The identifier of the paper this experiment is associated with, linking to the `papers` table (Foreign Key).

### `experiment_items`

This table details the items used in each experiment.

- **experiment_item_id**: A unique identifier for each experiment item (Primary Key).
- **experiment_id**: The identifier of the experiment, linking to the `experiments` table (Foreign Key).
- **material_id**: The identifier of the material used, linking to the `materials` table (Foreign Key).
- **supplier_id**: The identifier of the supplier of the material, linking to the `suppliers` table (Foreign Key).
- **usage**: A description of how the material is used in the experiment.

### Junction Tables

#### `paper_authors`

A many-to-many relationship table linking papers and authors.

- **paper_id**: The identifier of the paper (Foreign Key).
- **author_id**: The identifier of the author (Foreign Key).

#### `paper_tags`

A many-to-many relationship table linking papers and tags.

- **paper_id**: The identifier of the paper (Foreign Key).
- **tag_id**: The identifier of the tag (Foreign Key).

#### `paper_methodologies`

A many-to-many relationship table linking papers and methodologies.

- **paper_id**: The identifier of the paper (Foreign Key).
- **methodology_id**: The identifier of the methodology (Foreign Key).

---

## Conclusion

NexusGraph is a versatile tool for researchers, enabling efficient organization and access to academic papers. Developers can utilize the provided schema to build applications that leverage its rich features. For further information or inquiries, please feel free to engage in a dialogue or ask questions.
