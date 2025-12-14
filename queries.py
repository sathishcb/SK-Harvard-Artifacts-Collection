SQL_QUERIES={
    # ---------- artifact_metadata ----------
    "1. 11th century Byzantine artifacts":
        "SELECT * FROM artifact_metadata WHERE century='11th century' AND culture='Byzantine'",

    "2. Unique cultures represented":
        "SELECT DISTINCT culture FROM artifact_metadata WHERE culture IS NOT NULL",

    "3. Artifacts from Archaic Period":
        "SELECT * FROM artifact_metadata WHERE period='Archaic'",

    "4. Titles ordered by accession year (DESC)":
        "SELECT title, accessionyear FROM artifact_metadata ORDER BY accessionyear DESC",

    "5. Artifacts count per department":
        "SELECT department, COUNT(*) AS total FROM artifact_metadata GROUP BY department",

    "6. Oldest 20 artifacts (by accession year)":
        "SELECT * FROM artifact_metadata ORDER BY accessionyear ASC LIMIT 20",


    # ---------- artifact_media ----------
    "7. Artifacts with more than 1 image":
        """
        SELECT am.title, m.imagecount 
        FROM artifact_media m
        JOIN artifact_metadata am ON am.id = m.objectid
        WHERE m.imagecount > 1
        """,

    "8. Average rank of all artifacts":
        "SELECT AVG(`rank`) AS avg_rank FROM artifact_media",

    "9. Artifacts where colorcount > mediacount":
        """
        SELECT am.title, m.colorcount, m.mediacount
        FROM artifact_metadata am
        JOIN artifact_media m ON am.id = m.objectid
        WHERE m.colorcount > m.mediacount
        """,

    "10. Artifacts created between 1500 and 1600":
        """
        SELECT am.title, m.datebegin, m.dateend 
        FROM artifact_metadata am
        JOIN artifact_media m ON am.id = m.objectid
        WHERE m.datebegin >= 1500 AND m.dateend <= 1600
        """,

    "11. Artifacts with no media files":
        "SELECT COUNT(*) AS no_media FROM artifact_media WHERE mediacount = 0 OR mediacount IS NULL",

    "12. Maximum imagecount per classification":
        """
        SELECT am.classification, MAX(m.imagecount) AS max_images
        FROM artifact_media m
        JOIN artifact_metadata am ON am.id = m.objectid
        GROUP BY am.classification
        """,


    # ---------- artifact_colors ----------
    "13. All distinct hues used":
        "SELECT DISTINCT hue FROM artifact_colors WHERE hue IS NOT NULL",

    "14. Top 5 most used colors":
        """
        SELECT color, COUNT(*) AS frequency
        FROM artifact_colors
        GROUP BY color
        ORDER BY frequency DESC
        LIMIT 5
        """,

    "15. Average coverage percent for each hue":
        """
        SELECT hue, AVG(percent) AS avg_percent
        FROM artifact_colors
        GROUP BY hue
        """,

    "16. Colors used for a given artifact ID":
        "SELECT * FROM artifact_colors WHERE objectid = :id",

    "17. Total number of color entries":
        "SELECT COUNT(*) AS total_colors FROM artifact_colors",

    "18. Hue frequency per classification":
        """
        SELECT am.classification, c.hue, COUNT(*) AS hue_count
        FROM artifact_colors c
        JOIN artifact_metadata am ON am.id = c.objectid
        GROUP BY am.classification, c.hue
        """,


    # ---------- JOIN Queries ----------
    "19. Artifact titles + hues (Byzantine culture)":
        """
        SELECT am.title, c.hue
        FROM artifact_metadata am
        JOIN artifact_colors c ON am.id = c.objectid
        WHERE am.culture = 'Byzantine'
        """,

    "20. Each artifact title with all hues":
        """
        SELECT am.title, c.hue
        FROM artifact_metadata am
        JOIN artifact_colors c ON am.id = c.objectid
        ORDER BY am.title
        """,

    "21. Titles, cultures, and ranks (period NOT NULL)":
        """
        SELECT am.title, am.culture, m.`rank`
        FROM artifact_metadata am
        JOIN artifact_media m ON am.id = m.objectid
        WHERE am.period IS NOT NULL
        """,

    "22. Top 10 ranked artifacts that include hue 'Grey'":
        """
        SELECT DISTINCT am.title, m.`rank`
        FROM artifact_metadata am
        JOIN artifact_media m ON am.id = m.objectid
        JOIN artifact_colors c ON am.id = c.objectid
        WHERE c.hue = 'Grey'
        ORDER BY m.`rank`
        LIMIT 10
        """,

    "23. Artifacts per classification + average media count":
        """
        SELECT am.classification, COUNT(*) AS total_artifacts,
               AVG(m.mediacount) AS avg_media
        FROM artifact_metadata am
        JOIN artifact_media m ON am.id = m.objectid
        GROUP BY am.classification
        """,

    "24. Count artifacts grouped by century":
        """
        SELECT century, COUNT(*) AS total
        FROM artifact_metadata
        GROUP BY century
        ORDER BY century
        """,

    "25. Most common hue used per classification":
        """
        SELECT am.classification, c.hue, COUNT(*) AS hue_count
        FROM artifact_colors c
        JOIN artifact_metadata am ON am.id = c.objectid
        GROUP BY am.classification, c.hue
        ORDER BY hue_count DESC
        """
}
<content omitted placeholder>
