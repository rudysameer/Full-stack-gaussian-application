
from backend.services.progress_parser_colmap import ( 
    ColmapProgressParser,
)
parser = ColmapProgressParser(total_images=148)


lines = [
    "===== STEP 1/3 =====",

    "Processed file [1/148]",
    "Processed file [50/148]",
    "Processed file [101/148]",
    "Processed file [148/148]",

    "===== STEP 1 COMPLETED =====",

    "===== STEP 2/3 =====",

    "Matching block [1/3, 1/3]",
    "Matching block [1/3, 2/3]",
    "Matching block [1/3, 3/3]",
    "Matching block [2/3, 1/3]",
    "Matching block [2/3, 2/3]",
    "Matching block [2/3, 3/3]",
    "Matching block [3/3, 1/3]",
    "Matching block [3/3, 2/3]",
    "Matching block [3/3, 3/3]",

    "===== STEP 2 COMPLETED =====",

    "===== STEP 3/3 =====",

    "Registering image #4 (3)",
    "Registering image #5 (4)",
    "Registering image #20 (19)",
    "Registering image #101 (147)",

    "Retriangulation",

    "Global bundle adjustment",

    "Registering image #102 (148)",

    "Retriangulation",

    "Global bundle adjustment",

    "===== STEP 3 COMPLETED =====",

    "===== PIPELINE COMPLETED =====",
]

off_lines = [
    "===== STEP 1/3 =====",

    "Feature extraction",
    "Processed file [50/148]",
    "Processed file [101/148]",
    "Processed file [148/148]",

    "===== STEP 1 COMPLETED =====",

    "Exhaustive feature matching",

    "Matching block [1/3, 1/3]",
    "Matching block [1/3, 2/3]",
    "Matching block [1/3, 3/3]",
    "Matching block [2/3, 1/3]",
    "Matching block [2/3, 2/3]",
    "Matching block [2/3, 3/3]",
    "Matching block [3/3, 1/3]",
    "Matching block [3/3, 2/3]",
    "Matching block [3/3, 3/3]",

    "===== STEP 2 COMPLETED =====",

    "Loading database",

    "Registering image #4 (3)",
    "Registering image #5 (4)",
    "Registering image #20 (19)",
    "Registering image #101 (147)",

    "Retriangulation",

    "Global bundle adjustment",

    "Registering image #102 (148)",

    "Retriangulation",

    "Global bundle adjustment",

    "Done.",
]




for line in off_lines:

    result = parser.parse(line)

    if result is not None:
        print(line)
        print(result)
        print()