import os
import shutil
import re
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import csv
import statistics
import glob
import pandas as pd
import matplotlib.pyplot as plt

# Ne menge chaoscode. Enthällt jeglichen Code den ich genutzt habe

# Die genaueren Gruppen der Bilder mit Textinhalt sind hier Definiert:
textMain = [11,12,13,16,17,128,129,130] # The text is the main part of the image. The background is not important.
textPic = [33,88,107,108,109,110,11,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,131,132,133,134,135,136,137,138,139,140,141] # Both image and text are important.
textBack = [15,34,74,76,82,84,85,87,92,99,100,102,106,] # The text is the background of the image. The main part is the image.
textOnly = [142,143,144,146,147,148,149,150,151,152,153] # Consists only of text, no image.
all_ids = set(textMain + textPic + textBack + textOnly) # Combine all IDs into one set for fast lookup

# memes gehören aufgrund iherer Bild und textbasierter natur immer zu textPic. Außerdem sind auch Zitate enthalten, 
# die sowohl das Zitat als auch das Bild der Person enthalten. Hier geht es nur um Zitate mit Bild der person, Zitate die lediglich mit einem namen als solches gekennzeichnet sind sind in textMain enthalten.
# Demnach werden diese beiden kategorieren noch ein mal seperat betrachtet.
memes = [107,108,109,110,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127]
quotes = [33,88,131,136,138,140] 
statement_face = [132,133,135] # statement and a face on the image. Composition of the picture similar to quotes.


#  Moves images from the current_images folder to the Text_pics folder, only if the image ID is in all_ids.
def move_pics():
    src_folder = r"C:/Coding/Git/EyesWideScroll/current_images"
    dst_folder = r"C:/Coding/Python_projects/Text_pics"
    for filename in os.listdir(src_folder):
        match = re.match(r"id0*([1-9]\d*)", filename)
        if not match:
            continue  # Skip files that don't match the pattern

        img_id = int(match.group(1))
        if img_id in all_ids:
            src_path = os.path.join(src_folder, filename)
            dst_path = os.path.join(dst_folder, filename)
            shutil.copy2(src_path, dst_path)

# Moves CSV files from the EyesWideScroll folder to the text_csv folder, only if the image ID is in all_ids.
def move_csv():
    src_folder = r"C:/Coding/Git/EyesWideScroll"
    dst_folder = r"C:/Coding/Python_projects/text_csv"
    for filename in os.listdir(src_folder):
        if not filename.endswith(".csv"):
            continue
        match = re.search(r"_id0*([1-9]\d*)_", filename)
        if not match:
            continue
        csv_id = int(match.group(1))
        if csv_id in all_ids:
            src_path = os.path.join(src_folder, filename)
            dst_path = os.path.join(dst_folder, filename)
            shutil.copy2(src_path, dst_path)

# Opens images from the Text_pics folder and allows the user to select areas of interest.
def get_picture_area():
    img_folder = r"C:/Coding/Python_projects/Text_pics"
    save_file = r"C:/Coding/Python_projects/areas.txt"
    img_files = [f for f in os.listdir(img_folder) if re.match(r"id0*([1-9]\d*)", f)]
    img_files.sort()  # Optional: sort for consistent order

    areas_dict = {}

    class ImageSelector:
        def __init__(self, master, img_files):
            self.master = master
            self.img_files = img_files
            self.idx = 0
            self.areas = []
            self.rect = None
            self.start_x = None
            self.start_y = None
            self.img_id = None

            self.canvas = tk.Canvas(master)
            self.canvas.pack()
            self.next_btn = tk.Button(master, text="Next Image", command=self.next_image)
            self.next_btn.pack()

            self.master.bind("<Escape>", lambda e: self.master.quit())
            self.load_image()

            self.canvas.bind("<ButtonPress-1>", self.on_press)
            self.canvas.bind("<B1-Motion>", self.on_drag)
            self.canvas.bind("<ButtonRelease-1>", self.on_release)

        def load_image(self):
            if self.idx >= len(self.img_files):
                self.save_areas()
                self.master.quit()
                return
            self.areas = []
            img_file = self.img_files[self.idx]
            self.img_id = re.match(r"id0*([1-9]\d*)", img_file).group(1)
            img_path = os.path.join(img_folder, img_file)
            self.img = Image.open(img_path)
            self.tk_img = ImageTk.PhotoImage(self.img)
            self.canvas.config(width=self.img.width, height=self.img.height)
            self.canvas.delete("rect")
            self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)
            self.master.geometry(f"{self.img.width}x{self.img.height+40}")

        def on_press(self, event):
            self.start_x = event.x
            self.start_y = event.y
            self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red", tag="rect")

        def on_drag(self, event):
            if self.rect:
                self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

        def on_release(self, event):
            x0, y0 = self.start_x, self.start_y
            x1, y1 = event.x, event.y
            x_start, x_end = sorted([x0, x1])
            y_start, y_end = sorted([y0, y1])

            x_start = max(0, min(800, x_start))
            y_start = max(0, min(800, y_start))
            x_end = max(0, min(800, x_end))
            y_end = max(0, min(800, y_end))

            self.areas.append(f"({x_start},{y_start})-({x_end},{y_end})")

        def next_image(self):
            if self.areas:
                areas_str = ";".join(self.areas)
                areas_dict[self.img_id] = areas_str
            self.idx += 1
            self.canvas.delete("rect")
            self.load_image()

        def save_areas(self):
            with open(save_file, "a") as f:
                for img_id, areas_str in areas_dict.items():
                    f.write(f"{img_id}:{areas_str}\n")

    if __name__ == "__main__":
        root = tk.Tk()
        root.title("Select Areas on Images")
        selector = ImageSelector(root, img_files)
        root.mainloop()

# How many percent of the gaze points are inside the areas for each imageID. Checks every person for the given imageID.
def percentage(imageID):
    # Load areas for the given imageID
    areas_file = r"C:/Coding/Python_projects/areas.txt"
    areas = []
    with open(areas_file, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith(str(imageID) + ":"):
                area_str = line.split(":", 1)[1]
                for area in area_str.split(";"):
                    match = re.match(r"\((\d+),(\d+)\)-\((\d+),(\d+)\)", area)
                    if match:
                        x_start, y_start, x_end, y_end = map(int, match.groups())
                        areas.append((x_start, y_start, x_end, y_end))
                break
    if not areas:
        return 0.0  # No areas found for this image

    # Find all CSV files for the imageID
    csv_folder = r"C:/Coding/Python_projects/text_csv"
    csv_files = []
    for fname in os.listdir(csv_folder):
        if re.search(r"_id0*{}[_\.]".format(imageID), fname) and fname.endswith(".csv"):
            csv_files.append(os.path.join(csv_folder, fname))
    if not csv_files:
        return 0.0  # No CSV files found
    
    # Check coordinates in all CSV files
    total = 0
    inside = 0
    for csv_file in csv_files:
        with open(csv_file, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                coord = row.get("left_gaze_point_on_display_area")
                
                if not coord or "," not in coord:
                    continue
                try:
                    x, y = map(float, coord.strip("()").split(","))

                    # gaze points are in range 0-1, convert to pixel coordinates
                    x = x*800
                    y = y*800
                except ValueError as e:
                    print(e.args[0]) 
                    continue
                total += 1
                for x_start, y_start, x_end, y_end in areas:
                    if x_start < x < x_end and y_start < y < y_end:
                        inside += 1
                        break
    return (inside / total * 100) if total > 0 else 0.0

# Calculates the percentage of gaze points inside the areas for all imageIDs and writes the results to a file.
def percentage_all():
    output_file = r"C:/Coding/Python_projects/percentages.txt"
    with open(output_file, "w") as f:
        for img_id in sorted(all_ids):
            percent = percentage(img_id)
            f.write(f"{img_id}: {percent:.2f}\n")

# Similar do percentage(), but checks the positions of the fixations instead of every gaze point.
# Fixations are more stable and less noisy than gaze points, so this might yield different results
def percentage_fixations(imageID):
    # Load areas for the given imageID
    areas_file = r"C:/Coding/Python_projects/areas.txt"
    areas = []
    with open(areas_file, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith(str(imageID) + ":"):
                area_str = line.split(":", 1)[1]
                for area in area_str.split(";"):
                    match = re.match(r"\((\d+),(\d+)\)-\((\d+),(\d+)\)", area)
                    if match:
                        x_start, y_start, x_end, y_end = map(int, match.groups())
                        areas.append((x_start, y_start, x_end, y_end))
                break
    if not areas:
        return 0.0  # No areas found for this image
    
    # Find all CSV files for the imageID
    csv_folder = r"C:/Coding/Git/EyeTracking_basti/fixations"
    csv_files = []
    for fname in os.listdir(csv_folder):
        if re.search(r"_id0*{}[_\.]".format(imageID), fname) and fname.endswith(".csv"):
            csv_files.append(os.path.join(csv_folder, fname))
    if not csv_files:
        return 0.0  # No CSV files found
    
    # Check coordinates in all CSV files
    total = 0
    inside = 0
    for csv_file in csv_files:
        with open(csv_file, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                x = float(row.get("x"))
                y = float(row.get("y"))
                #coord = row.get("left_gaze_point_on_display_area")
                
                if not x or not y:
                    continue

                total += 1
                for x_start, y_start, x_end, y_end in areas:
                    if x_start < x < x_end and y_start < y < y_end:
                        inside += 1
                        break
    return (inside / total * 100) if total > 0 else 0.0

def percentage_fixations_all():
    output_file = r"C:/Coding/Python_projects/percentages_fixations.txt"
    with open(output_file, "w") as f:
        for img_id in sorted(all_ids):
            percent = percentage_fixations(img_id)
            f.write(f"{img_id}: {percent:.2f}\n")

# just some fix to the areas.txt file, so that the coordinates are always in the range 0-800. Previously, some coordinates were outside this range, which caused problems in the analysis.
def fix_area():
    check_file = r"C:/Coding/Python_projects/areas.txt"
    new_file = r"C:/Coding/Python_projects/areas_fixed.txt"
    with open(check_file, "r") as f:
        lines = f.readlines()
        fixed_lines = []
        for line in lines:
            match = re.match(r"(\d+):(.*)", line)
            if not match:
                fixed_lines.append(line)
                continue
            img_id, areas_str = match.groups()
            fixed_areas = []
            for area in areas_str.split(";"):
                coords_match = re.match(r"\((\-?\d+),(\-?\d+)\)-\((\-?\d+),(\-?\d+)\)", area)
                if coords_match:
                    x_start, y_start, x_end, y_end = map(int, coords_match.groups())
                    x_start = max(0, min(800, x_start))
                    y_start = max(0, min(800, y_start))
                    x_end = max(0, min(800, x_end))
                    y_end = max(0, min(800, y_end))
                    fixed_areas.append(f"({x_start},{y_start})-({x_end},{y_end})")
            if fixed_areas:
                fixed_lines.append(f"{img_id}:{';'.join(fixed_areas)}\n")
            else:
                fixed_lines.append(line)

        with open(new_file, "w") as f_out:
            f_out.writelines(fixed_lines)

# compares results from percentage_fixations_all() with the results from percentage_all()
# and creates a .csv file with the results
def compare():
    perc_file = r"C:/Coding/Python_projects/percentages.txt"
    fix_file = r"C:/Coding/Python_projects/percentages_fixations.txt"
    portion_file = r"C:/Coding/Python_projects/text_portion.txt"
    out_file = r"C:/Coding/Python_projects/compare_fixations.csv"

    # Read percentages.txt
    perc_dict = {}
    with open(perc_file, "r") as f:
        for line in f:
            if ":" in line:
                img_id, perc = line.strip().split(":")
                perc_dict[int(img_id)] = float(perc.strip())

    # Read percentages_fixations.txt
    fix_dict = {}
    with open(fix_file, "r") as f:
        for line in f:
            if ":" in line:
                img_id, perc = line.strip().split(":")
                fix_dict[int(img_id)] = float(perc.strip())

    # Read text_portion.txt
    portion_dict = {}
    with open(portion_file, "r") as f:
        for line in f:
            if ":" in line:
                img_id, portion = line.strip().split(":")
                portion_dict[int(img_id)] = float(portion.strip())

    # Write compare_fixations.csv
    with open(out_file, "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "id",
            "percentage",
            "percentage_fixations",
            "difference",
            "text_portion",
            "percentage_fixations/text_portion"
        ])
        ids = sorted(perc_dict.keys())
        fix_values = []
        perc_values = []
        diff_values = []
        portion_values = []
        ratio_values = []

        for img_id in ids:
            perc = perc_dict.get(img_id, 0.0)
            fix = fix_dict.get(img_id, 0.0)
            portion = portion_dict.get(img_id, 0.0)
            diff = fix - perc
            ratio = fix / portion if portion > 0 else 0.0

            fix_values.append(fix)
            perc_values.append(perc)
            diff_values.append(diff)
            portion_values.append(portion)
            ratio_values.append(ratio)

            writer.writerow([
                img_id,
                f"{perc:.2f}",
                f"{fix:.2f}",
                f"{diff:.2f}",
                f"{portion:.4f}",
                f"{ratio:.2f}"
            ])

        # Mean row
        writer.writerow([
            "mean",
            f"{statistics.mean(perc_values):.2f}",
            f"{statistics.mean(fix_values):.2f}",
            f"{statistics.mean(diff_values):.2f}",
            f"{statistics.mean(portion_values):.4f}",
            f"{statistics.mean(ratio_values):.2f}"
        ])

        # Median row
        writer.writerow([
            "median",
            f"{statistics.median(perc_values):.2f}",
            f"{statistics.median(fix_values):.2f}",
            f"{statistics.median(diff_values):.2f}",
            f"{statistics.median(portion_values):.4f}",
            f"{statistics.median(ratio_values):.2f}"
        ])

# The groups are definded at the top of the file. This function compares the results of different values for each group. 
def compare_groups():
    compare_file = r"C:/Coding/Python_projects/compare_fixations.csv"
    out_file = r"C:/Coding/Python_projects/compare_groups.csv"

    # Read compare_fixations.csv
    data = {}
    with open(compare_file, "r", newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                img_id = int(row["id"])
            except ValueError:
                continue  # skip mean/median rows
            data[img_id] = {
                "percentage": float(row["percentage"]),
                "percentage_fixations": float(row["percentage_fixations"]),
                "difference": float(row["difference"]),
                "text_portion": float(row["text_portion"]),
                "percentage_fixations/text_portion": float(row["percentage_fixations/text_portion"])
            }

    groups = {
        "textMain": textMain,
        "textPic": textPic,
        "-memes": memes,
        "-quotes": quotes,
        "textBack": textBack,
        "textOnly": textOnly
    }

    with open(out_file, "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        # First: mean section
        writer.writerow([
            "group",
            "mean percentage",
            "var percentage",
            "mean percentage_fixations",
            "var percentage_fixations",
            "mean difference",
            "mean text_portion",
            "var text_portion",
            "mean percentage_fixations/text_portion",
            "var percentage_fixations/text_portion"
        ])
        for group_name, ids in groups.items():
            perc_values = [data.get(img_id, {}).get("percentage", 0.0) for img_id in ids]
            fix_values = [data.get(img_id, {}).get("percentage_fixations", 0.0) for img_id in ids]
            diff_values = [data.get(img_id, {}).get("difference", 0.0) for img_id in ids]
            text_portion_values = [data.get(img_id, {}).get("text_portion", 0.0) for img_id in ids]
            ratio_values = [data.get(img_id, {}).get("percentage_fixations/text_portion", 0.0) for img_id in ids]

            mean_perc = statistics.mean(perc_values) if perc_values else 0.0
            var_perc = statistics.variance(perc_values) if len(perc_values) > 1 else 0.0
            mean_fix = statistics.mean(fix_values) if fix_values else 0.0
            var_fix = statistics.variance(fix_values) if len(fix_values) > 1 else 0.0
            mean_diff = statistics.mean(diff_values) if diff_values else 0.0
            mean_text_portion = statistics.mean(text_portion_values) if text_portion_values else 0.0
            var_text_portion = statistics.variance(text_portion_values) if len(text_portion_values) > 1 else 0.0
            mean_ratio = statistics.mean(ratio_values) if ratio_values else 0.0
            var_ratio = statistics.variance(ratio_values) if len(ratio_values) > 1 else 0.0

            writer.writerow([
                group_name,
                f"{mean_perc:.2f}",
                f"{var_perc:.2f}",
                f"{mean_fix:.2f}",
                f"{var_fix:.2f}",
                f"{mean_diff:.2f}",
                f"{mean_text_portion:.4f}",
                f"{var_text_portion:.4f}",
                f"{mean_ratio:.2f}",
                f"{var_ratio:.2f}"
            ])

        # Empty row
        writer.writerow([])

        # Second: median section
        writer.writerow([
            "group",
            "median percentage",
            "var percentage (median)",
            "median percentage_fixations",
            "var percentage_fixations (median)",
            "median difference",
            "median text_portion",
            "var text_portion (median)",
            "median percentage_fixations/text_portion",
            "var percentage_fixations/text_portion (median)"
        ])
        for group_name, ids in groups.items():
            perc_values = [data.get(img_id, {}).get("percentage", 0.0) for img_id in ids]
            fix_values = [data.get(img_id, {}).get("percentage_fixations", 0.0) for img_id in ids]
            diff_values = [data.get(img_id, {}).get("difference", 0.0) for img_id in ids]
            text_portion_values = [data.get(img_id, {}).get("text_portion", 0.0) for img_id in ids]
            ratio_values = [data.get(img_id, {}).get("percentage_fixations/text_portion", 0.0) for img_id in ids]

            median_perc = statistics.median(perc_values) if perc_values else 0.0
            var_perc_median = statistics.variance(perc_values) if len(perc_values) > 1 else 0.0
            median_fix = statistics.median(fix_values) if fix_values else 0.0
            var_fix_median = statistics.variance(fix_values) if len(fix_values) > 1 else 0.0
            median_diff = statistics.median(diff_values) if diff_values else 0.0
            median_text_portion = statistics.median(text_portion_values) if text_portion_values else 0.0
            var_text_portion_median = statistics.variance(text_portion_values) if len(text_portion_values) > 1 else 0.0
            median_ratio = statistics.median(ratio_values) if ratio_values else 0.0
            var_ratio_median = statistics.variance(ratio_values) if len(ratio_values) > 1 else 0.0

            writer.writerow([
                group_name,
                f"{median_perc:.2f}",
                f"{var_perc_median:.2f}",
                f"{median_fix:.2f}",
                f"{var_fix_median:.2f}",
                f"{median_diff:.2f}",
                f"{median_text_portion:.4f}",
                f"{var_text_portion_median:.4f}",
                f"{median_ratio:.2f}",
                f"{var_ratio_median:.2f}"
            ])

# Calculates the portion of the image that is text for a given imageID.
def text_portion(imageID):

    areas_file = r"C:/Coding/Python_projects/areas.txt"
    total_area = 800 * 800
    text_area = 0

    with open(areas_file, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith(str(imageID) + ":"):
                area_str = line.split(":", 1)[1]
                for area in area_str.split(";"):
                    match = re.match(r"\((\d+),(\d+)\)-\((\d+),(\d+)\)", area)
                    if match:
                        x_start, y_start, x_end, y_end = map(int, match.groups())
                        width = abs(x_end - x_start)
                        height = abs(y_end - y_start)
                        text_area += width * height
                break

    portion = text_area / total_area if total_area > 0 else 0.0
    return portion

# Calculates the text portion for all imageIDs and writes the results to a file.
def text_portion_all():
    output_file = r"C:/Coding/Python_projects/text_portion.txt"
    with open(output_file, "w") as f:
        for img_id in sorted(all_ids):
            portion = text_portion(img_id)
            f.write(f"{img_id}: {portion:.4f}\n")

def fixation_timing():
    areas_file = r"C:/Coding/Python_projects/areas.txt"
    fix_folder = r"C:/Coding/Git/EyeTracking_basti/fixations"
    output_file = r"C:/Coding/Python_projects/fixation_timing.csv"

    # Load areas for all imageIDs
    areas_dict = {}
    with open(areas_file, "r") as f:
        for line in f:
            line = line.strip()
            match = re.match(r"(\d+):(.*)", line)
            if not match:
                continue
            img_id, areas_str = match.groups()
            areas = []
            for area in areas_str.split(";"):
                coords_match = re.match(r"\((\d+),(\d+)\)-\((\d+),(\d+)\)", area)
                if coords_match:
                    x_start, y_start, x_end, y_end = map(int, coords_match.groups())
                    areas.append((x_start, y_start, x_end, y_end))
            if areas:
                areas_dict[int(img_id)] = areas

    # For each imageID, collect all fixations for each file and check if they're in area
    results = {}  # {img_id: [[0/1, 0/1, ...], ...]}
    max_fix_count = {}  # {img_id: max number of fixations found}
    for fix_file in glob.glob(os.path.join(fix_folder, "*.csv")):
        fname = os.path.basename(fix_file)
        match = re.search(r"_id0*([1-9]\d*)[_\.]", fname)
        if not match:
            continue
        img_id = int(match.group(1))
        if img_id not in areas_dict:
            continue
        areas = areas_dict[img_id]
        fix_in_area = []
        with open(fix_file, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    x = float(row.get("x"))
                    y = float(row.get("y"))
                except (TypeError, ValueError):
                    in_area = 0
                else:
                    in_area = 0
                    for x_start, y_start, x_end, y_end in areas:
                        if x_start < x < x_end and y_start < y < y_end:
                            in_area = 1
                            break
                fix_in_area.append(in_area)
        if img_id not in results:
            results[img_id] = []
            max_fix_count[img_id] = 0
        results[img_id].append(fix_in_area)
        if len(fix_in_area) > max_fix_count[img_id]:
            max_fix_count[img_id] = len(fix_in_area)

    # Calculate percentage for each fixation index for each imageID
    with open(output_file, "w", newline='') as csvfile:
        # Write header: id | fixation 1 | fixation 2 | ...
        max_fix = max(max_fix_count.values()) if max_fix_count else 0
        headers = ["id"] + [f"fixation {i+1}" for i in range(max_fix)]
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        # Collect all percentages for each fixation index for stats
        all_percentages = [[] for _ in range(max_fix)]
        for img_id in sorted(results.keys()):
            fix_lists = results[img_id]
            row = [img_id]
            for i in range(max_fix_count[img_id]):
                values = [fix[i] for fix in fix_lists if len(fix) > i]
                percent = (sum(values) / len(values) * 100) if values else 0.0
                row.append(f"{percent:.2f}")
                if i < max_fix:
                    all_percentages[i].append(percent)
            writer.writerow(row)
        # Add mean, median, var rows
        mean_row = ["mean"]
        median_row = ["median"]
        var_row = ["var"]
        for col in all_percentages:
            mean_row.append(f"{statistics.mean(col):.2f}" if col else "")
            median_row.append(f"{statistics.median(col):.2f}" if col else "")
            var_row.append(f"{statistics.variance(col):.2f}" if len(col) > 1 else "")
        writer.writerow(mean_row)
        writer.writerow(median_row)
        writer.writerow(var_row)

def timing_groups():

    timing_file = r"C:/Coding/Python_projects/fixation_timing.csv"
    out_file = r"C:/Coding/Python_projects/timing_groups.csv"

    # Read fixation_timing.csv
    data = {}
    with open(timing_file, "r", newline='') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        for row in reader:
            try:
                img_id = int(row["id"])
            except ValueError:
                continue  # skip mean/median/var rows
            data[img_id] = [float(row[h]) for h in headers[1:] if row[h]]

    groups = {
        "textMain": textMain,
        "textPic": textPic,
        "-memes": memes,
        "-quotes": quotes,
        "textBack": textBack,
        "textOnly": textOnly
    }

    # Determine max number of fixations
    max_fix = max((len(vals) for vals in data.values()), default=0)

    with open(out_file, "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Header
        header = ["group"]
        for i in range(max_fix):
            header += [f"fix{i+1}_mean", f"fix{i+1}_median", f"fix{i+1}_var"]
        writer.writerow(header)

        for group_name, ids in groups.items():
            # Collect fixation values for each fixation index
            fix_lists = [[] for _ in range(max_fix)]
            for img_id in ids:
                vals = data.get(img_id, [])
                for i in range(len(vals)):
                    fix_lists[i].append(vals[i])
            row = [group_name]
            for fix_vals in fix_lists:
                if fix_vals:
                    row.append(f"{statistics.mean(fix_vals):.2f}")
                    row.append(f"{statistics.median(fix_vals):.2f}")
                    row.append(f"{statistics.variance(fix_vals):.2f}" if len(fix_vals) > 1 else "0.00")
                else:
                    row += ["", "", ""]
            writer.writerow(row)


def show_group_percentages():
    csv_file = r"C:/Coding/Python_projects/compare_groups.csv"
    groups = []
    mean_percentage = []
    mean_percentage_fixations = []

    # Read only the first section (mean rows) from the CSV
    with open(csv_file, "r", newline='') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if not row or row[0] == "":  # Stop at empty row (before median section)
                break
            groups.append(row[0])
            mean_percentage.append(float(row[1]))
            mean_percentage_fixations.append(float(row[3]))

    x = range(len(groups))
    width = 0.35

    fig, ax = plt.subplots()
    ax.bar([i - width/2 for i in x], mean_percentage, width, label='Mean Percentage', color='skyblue')
    ax.bar([i + width/2 for i in x], mean_percentage_fixations, width, label='Mean Percentage Fixations', color='orange')

    ax.set_xticks(x)
    ax.set_xticklabels(groups, rotation=45, ha='right')
    ax.set_ylabel('Percentage')
    ax.set_title('Mean Percentage vs Mean Percentage Fixations by Group')
    ax.legend()
    plt.tight_layout()
    plt.show()

def show_group_portion():
    csv_file = r"C:/Coding/Python_projects/compare_groups.csv"
    groups = []
    mean_text_portion = []
    var_text_portion = []

    # Read only the first section (mean rows) from the CSV
    with open(csv_file, "r", newline='') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if not row or row[0] == "":
                break
            groups.append(row[0])
            mean_text_portion.append(float(row[6]))
            var_text_portion.append(float(row[7]))

    x = range(len(groups))
    width = 0.35

    fig, ax = plt.subplots()
    ax.bar([i - width/2 for i in x], mean_text_portion, width, label='Mean Text Portion', color='lightgreen')
    ax.bar([i + width/2 for i in x], var_text_portion, width, label='Variance Text Portion', color='salmon')

    ax.set_xticks(x)
    ax.set_xticklabels(groups, rotation=45, ha='right')
    ax.set_ylabel('Text Portion')
    ax.set_title('Mean and Variance of Text Portion by Group')
    ax.legend()
    plt.tight_layout()
    plt.show()

def show_grouped_fixation_timing():
    csv_file = r"C:/Coding/Python_projects/timing_groups.csv"
    df = pd.read_csv(csv_file)
    # Only use group rows (skip mean/median/var if present)
    group_rows = df[~df['group'].isin(['mean', 'median', 'var'])]

    # Find all fixation columns with '_median' in their name
    fixation_median_cols = [col for col in df.columns if '_median' in col]

    fig, ax = plt.subplots()
    for idx, row in group_rows.iterrows():
        medians = [float(row[col]) if row[col] != "" else 0.0 for col in fixation_median_cols]
        ax.plot(range(1, len(medians)+1), medians, marker='o', label=row['group'])

    ax.set_xlabel('Fixation Number')
    ax.set_ylabel('Median Percentage in Area')
    ax.set_title('Median Percentage in Area by Fixation and Group')
    ax.legend()
    plt.tight_layout()
    plt.show()
