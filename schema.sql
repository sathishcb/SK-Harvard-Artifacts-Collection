CREATE DATABASE IF NOT EXISTS harvard_artifacts;
USE harvard_artifacts;

CREATE TABLE IF NOT EXISTS artifact_metadata (
    id INT PRIMARY KEY,
    title TEXT,
    culture TEXT,
    period TEXT,
    century TEXT,
    medium TEXT,
    dimensions TEXT,
    description TEXT,
    department TEXT,
    classification TEXT,
    accessionyear INT,
    accessionmethod TEXT
);

CREATE TABLE IF NOT EXISTS artifact_media (
    objectid INT PRIMARY KEY,
    imagecount INT,
    mediacount INT,
    colorcount INT,
    `rank` INT,
    datebegin INT,
    dateend INT,
    FOREIGN KEY (objectid) REFERENCES artifact_metadata(id)
);


CREATE TABLE IF NOT EXISTS artifact_colors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    objectid INT,
    color TEXT,
    spectrum TEXT,
    hue TEXT,
    percent DOUBLE,
    css3 TEXT,
    FOREIGN KEY (objectid) REFERENCES artifact_metadata(id)
);
