import os
from PIL import Image


DATASET_DIR = "dataset"

VALID_EXTENSIONS = (
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".gif",
    ".webp"
)


print("=" * 60)
print("CHECKING DATASET")
print("=" * 60)


if not os.path.exists(DATASET_DIR):
    print("ERROR: dataset folder not found.")
    exit()


total = 0
valid = 0
invalid = 0


for root, dirs, files in os.walk(DATASET_DIR):

    for filename in files:

        filepath = os.path.join(
            root,
            filename
        )

        total += 1

        # -----------------------------------------
        # Extension check
        # -----------------------------------------

        if not filename.lower().endswith(
            VALID_EXTENSIONS
        ):

            print(
                f"[INVALID EXTENSION] {filepath}"
            )

            invalid += 1
            continue


        # -----------------------------------------
        # PIL image check
        # -----------------------------------------

        try:

            with Image.open(filepath) as img:

                img.verify()


            # Open again after verify
            with Image.open(filepath) as img:

                img.load()


            print(
                f"[VALID] {filepath}"
            )

            valid += 1


        except Exception as e:

            print(
                f"[INVALID IMAGE] {filepath}"
            )

            print(
                f"    Reason: {e}"
            )

            invalid += 1


print("\n" + "=" * 60)
print("DATASET RESULT")
print("=" * 60)

print(
    f"Total files   : {total}"
)

print(
    f"Valid images  : {valid}"
)

print(
    f"Invalid files : {invalid}"
)

print("=" * 60)


if invalid == 0:

    print(
        "ALL IMAGES ARE VALID."
    )

else:

    print(
        "REMOVE OR REPLACE THE INVALID FILES."
    )