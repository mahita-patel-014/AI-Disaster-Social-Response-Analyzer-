import os
import shutil
from PIL import Image


SOURCE = "dataset"
DESTINATION = "clean_dataset"

VALID_EXTENSIONS = (
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
    ".gif"
)


if not os.path.exists(SOURCE):
    raise FileNotFoundError(
        f"Dataset folder not found: {os.path.abspath(SOURCE)}"
    )


# Remove old clean dataset
if os.path.exists(DESTINATION):
    shutil.rmtree(DESTINATION)

os.makedirs(DESTINATION)


total = 0
valid = 0
invalid = 0


print("=" * 70)
print("AI CP DISASTER - DATASET PREPARATION")
print("=" * 70)


for class_name in sorted(os.listdir(SOURCE)):

    source_class = os.path.join(
        SOURCE,
        class_name
    )

    if not os.path.isdir(source_class):
        continue

    destination_class = os.path.join(
        DESTINATION,
        class_name
    )

    os.makedirs(
        destination_class,
        exist_ok=True
    )

    print()
    print(f"CLASS: {class_name}")

    counter = 1


    for filename in sorted(
        os.listdir(source_class)
    ):

        source_file = os.path.join(
            source_class,
            filename
        )

        if not os.path.isfile(source_file):
            continue

        total += 1

        extension = os.path.splitext(
            filename
        )[1].lower()


        if extension not in VALID_EXTENSIONS:

            print(
                "[SKIPPED - NOT IMAGE]",
                filename
            )

            invalid += 1
            continue


        try:

            with Image.open(source_file) as image:

                # Force PIL to completely decode image
                image.load()

                # Convert to RGB
                image = image.convert("RGB")

                destination_file = os.path.join(
                    destination_class,
                    f"{counter}.jpg"
                )

                image.save(
                    destination_file,
                    "JPEG",
                    quality=95
                )


            print(
                "[VALID]",
                filename,
                "->",
                f"{counter}.jpg"
            )

            counter += 1
            valid += 1


        except Exception as error:

            print(
                "[INVALID]",
                filename,
                "|",
                error
            )

            invalid += 1


print()
print("=" * 70)
print("DATASET PREPARATION COMPLETE")
print("=" * 70)

print("Total files :", total)
print("Valid files :", valid)
print("Invalid     :", invalid)
print(
    "Clean dataset:",
    os.path.abspath(DESTINATION)
)

print("=" * 70)