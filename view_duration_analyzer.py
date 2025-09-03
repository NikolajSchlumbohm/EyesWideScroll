#aggregates view duration data
# measures view duration for stimuli and participants
# analyzes view duration patterns for grouped data
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
view_duration_df = pd.read_csv('view_durations.csv')

#Test: should be between 5-15
print("lowest Duration: ",view_duration_df["system_time_diff_seconds"].min())
# --> !!
print("highest Duration: ",view_duration_df["system_time_diff_seconds"].max())

#---General statistics
print("Mean Duration: ",view_duration_df["system_time_diff_seconds"].mean())
print("Median Duration: ",view_duration_df["system_time_diff_seconds"].median())
#each image name is formatted like id<image_id>_<tag1_<tag2>..._.jpg
#image_tag_dictionary should contain a list of tags for every image
#group view_durations_df by image id and dissect image_nam

def create_image_tag_dict(data):
    image_tag_dict = {}
    for file in data['image_name']:
        tags = file.split('_')[1:-1]  # Exclude 'id' and '.jpg'
        if "ncc" in tags:
            tags.remove("ncc")
        
        image_id = int(file.split('_')[0][2:])  # Extract image_id from 'id<image_id>'
        if len(tags)<1:
            #error in image namng - bandaid solution
            image_tag_dict[image_id] = ["text"]
        else:
            image_tag_dict[image_id] = tags
    print("image_tag_dict", image_tag_dict)
    return image_tag_dict

#--Group by image_name

#--Group by participant_id
#--Group by tag

#plot system_time_diff_seconds with different lines for each participant for all images by increasing id on the x-axis
def plot_participants():
    for participant_id in range(1,10):
        participant_data = view_duration_df[view_duration_df['participant_id'] == participant_id]
        print(f"Participant {participant_id} Data:\n", participant_data)
        plt.plot(participant_data['image_id'], participant_data['system_time_diff_seconds'], label=f'Participant {participant_id}')
        
    plt.xlabel('Image Name')
    plt.ylabel('System Time Diff (seconds)')
    plt.title(f'System Time Diff for Participant {participant_id}')
    plt.xticks(rotation=90)
    plt.show()

def view_duration_images(data):
    grouped_by_image = data.groupby('image_id').agg({
        'system_time_diff_seconds': ['mean', 'median', 'min', 'max'],
        'device_time_diff_seconds': ['mean', 'median', 'min', 'max']
    }).reset_index()
    return grouped_by_image

#plot view duration for images with image id on the x-axis and median view duration on the y-axis
def plot_view_duration_images():
    image_data = view_duration_images(view_duration_df)
    plt.bar(image_data['image_id'], image_data['system_time_diff_seconds']['median'])
    plt.xlabel('Image ID')
    plt.ylabel('Median System Time Diff (seconds)')
    plt.title('Median System Time Diff for Images')
    plt.show()


#print id and median time of image that is the minimum of median system_time_diff_seconds
min_image = view_duration_images(view_duration_df).sort_values(by=('system_time_diff_seconds', 'median')).iloc[0]
max_image = view_duration_images(view_duration_df).sort_values(by=('system_time_diff_seconds', 'median')).iloc[-1]
print("Image ID with Minimum Median System Time Diff (seconds):", min_image['image_id'])
print("Minimum Median System Time Diff (seconds):", min_image['system_time_diff_seconds']['median'])
print("Image ID with Maximum Median System Time Diff (seconds):", max_image['image_id'])
print("Maximum Median System Time Diff (seconds):", max_image['system_time_diff_seconds']['median'])

def analyze_tag_groups(data, only_text=False):
    # Create a dictionary to group images by their tag combinations
    tag_group_dict = {}
    
    # Group images by their tag combinations
    for image_id, tags in create_image_tag_dict(data).items():
        tag_combination = tuple(sorted(tags))  # Use sorted tuple for consistent grouping
        if tag_combination not in tag_group_dict:
            tag_group_dict[tag_combination] = []
        if (only_text and 'text' in tag_combination or 'textimg' in tag_combination) or not only_text:
            tag_group_dict[tag_combination].append(image_id)
        
    
    # Analyze each tag group
    tag_group_analysis = []
    
    for tag_combination, image_ids in tag_group_dict.items():
        # Filter data for images in this tag group
        tag_group_data = data[data['image_id'].isin(image_ids)]
        
        if not tag_group_data.empty:
            analysis = {
                'tag_combination': tag_combination,
                'tag_string': '_'.join(tag_combination),  # For easier reading
                'image_ids': image_ids,
                'image_count': len(image_ids),
                'total_observations': len(tag_group_data),
                'mean_system_time': tag_group_data['system_time_diff_seconds'].mean(),
                'median_system_time': tag_group_data['system_time_diff_seconds'].median(),
                'std_system_time': tag_group_data['system_time_diff_seconds'].std(),
                'min_system_time': tag_group_data['system_time_diff_seconds'].min(),
                'max_system_time': tag_group_data['system_time_diff_seconds'].max()
            }
            tag_group_analysis.append(analysis)
    
    # Convert to DataFrame for easier analysis
    tag_analysis_df = pd.DataFrame(tag_group_analysis)
    
    # Sort by median system time
    tag_analysis_df = tag_analysis_df.sort_values('median_system_time', ascending=False)
    print("tag_analysis1", tag_analysis_df)
    return tag_analysis_df

# Usage and display
def display_tag_group_analysis(data,only_text=False):
    tag_analysis = analyze_tag_groups(data,only_text)
    
    print("\n" + "="*80)
    print("TAG GROUP ANALYSIS")
    print("="*80)
    
    print(f"Total tag groups found: {len(tag_analysis)}")
    print("\nTag groups ranked by mean viewing time:")
    print("-" * 80)
    
    for idx, row in tag_analysis.iterrows():
        print(f"Tag Group: {row['tag_string']}")
        print(f"  Images: {row['image_count']} (IDs: {row['image_ids']})")
        print(f"  Observations: {row['total_observations']}")
        print(f"  Mean time: {row['mean_system_time']:.2f}s")
        print(f"  Median time: {row['median_system_time']:.2f}s")
        print(f"  Std dev: {row['std_system_time']:.2f}s")
        print(f"  Range: {row['min_system_time']:.2f}s - {row['max_system_time']:.2f}s")
        print("-" * 40)
    
    return tag_analysis



# Plot tag groups by mean viewing time
def plot_tag_groups(data,only_text = False):
    tag_analysis = analyze_tag_groups(data,only_text)
    #bandaid solution for dropping falsely labeled data
    print("Analysis time:",tag_analysis)
    tag_analysis = tag_analysis.drop([1,2])
    #frag nicht mich wieso die Indizes so sind
    plt.figure(figsize=(12, 8))
    plt.barh(range(len(tag_analysis)), tag_analysis['median_system_time'])
    plt.yticks(range(len(tag_analysis)), tag_analysis['tag_string'])
    plt.xlabel('Median System Time Diff (seconds)')
    plt.title('Median Viewing Time by Tag Group')
    plt.tight_layout()
    plt.show()
def analyze_temporal_pattern():
    # for every participant, sort their viewing data by time 
    # every file name is formatted like this: Proband<probandID>_hour_minute_seconds_id<imgID>_tag1_tag2..._.csv

    for participant_id, group in view_duration_df.groupby('participant_id'):

        group = group.sort_values('timestamp')
        print(group)
        # plot the system time diff for each image
        plt.figure(figsize=(12, 6))
        plt.plot(group['timestamp'], group['system_time_diff_seconds'], marker='o')
        plt.title(f"Viewing Time Pattern for Participant {participant_id}")
        plt.xlabel('Timestamp')
        plt.ylabel('System Time Diff (seconds)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()


#analyze_temporal_pattern()

def create_view_time_matrix(data):
    # Create a matrix with semantic categories on the one axis and text/no-text on the other axis
    # images with text are marked with the tag textimg, images with text only are marked with the tag text
    semantic_categories = ["meme", "person", "politik", "ort"]
    tag_analysis_df = analyze_tag_groups(data)

    # Create the view time matrix
    view_time_matrix = pd.DataFrame(0, index=semantic_categories, columns=["text", "no_text"], dtype=int)
    print("tag analysis",tag_analysis_df)
    # for every tag combination in tag_analysis_df["tag_combination"]

    for idx, row in tag_analysis_df.iterrows():
        for category in semantic_categories:
            if category in row['tag_string']:
                if 'textimg' in row['tag_string']:
                    view_time_matrix.at[category, "text"] = row['median_system_time']
                elif 'textigm' in row['tag_string']:
                    #misspelled file name
                    pass
                else:
                   view_time_matrix.at[category, "no_text"] = row['median_system_time']
        if 'text' == row['tag_string']:
            view_time_matrix.at["Nur Text", "text"] = row['median_system_time']

    return view_time_matrix

def visualize_view_time_matrix(data):
    view_time_matrix = create_view_time_matrix(data)
    plt.figure(figsize=(10, 6))
    sns.heatmap(view_time_matrix, annot=True, cmap="YlGnBu", cbar_kws={'label': 'Mean Viewing Time (seconds)'})
    plt.title("Viewing Time Matrix")
    plt.xlabel("Text Presence")
    plt.ylabel("Semantic Categories")
    plt.show()
def create_category_matrix(data):
    semantic_categories = ["meme", "person", "politik", "ort"]
    tag_analysis_df = analyze_tag_groups(data)
    #NxN matrix with each semantic category on both axes. 
    # Each cell shows the average system time diff for the combined category n,m without text
    category_matrix = pd.DataFrame(0, index=semantic_categories, columns=semantic_categories, dtype=float)
    category_matrix = category_matrix.map(lambda x: (0,0))
    print(category_matrix)
    for idx, row in tag_analysis_df.iterrows():
        for category in semantic_categories:
            for other_category in semantic_categories:
                cell = category_matrix.at[category, other_category]
                if other_category in row['tag_string'] and category in row['tag_string']:
                    print(category, other_category)
                    if "text" not in row['tag_string']:
                        cell = (cell[0],row['median_system_time'])
                    else:
                        cell = (row['median_system_time'],cell[1])
                category_matrix.at[category, other_category]= cell
    print(category_matrix)
    return category_matrix

def plot_category_matrix(data):
    category_matrix = create_category_matrix(data)
    plt.figure(figsize=(10, 8))
    sns.heatmap(category_matrix, annot=True, cmap="YlGnBu", cbar_kws={'label': 'Mean Viewing Time (seconds)'})
    plt.title("Category Interaction Matrix (No Text)")
    plt.xlabel("Semantic Categories")
    plt.ylabel("Semantic Categories")
    plt.show()
def normalize_view_durations(data):
    # divide system time diff by the number of words as seen in words_per_image_dict on each image where the id is present in words_per_image_dict.
    words_per_image_dict = {
    124:24,
    128:19,
    106:12,
    107:6,
    108:27,
    109:7,
    110:12,
    111:5,
    112:9,
    113:22,
    114:3,
    115:7,
    116:17,
    117:6,
    118:23,
    119:16,
    120:26,
    121:11,
    122:7,
    123:4,
    124:14,
    125:17,
    127:5,
    129:10,
    130:25,
    131:16,
    132:12,
    133:10,
    134:24,
    135:3,
    136:25,
    137:4,
    138:23,
    139:14,
    140:22,
    141:45,
    142:14,
    143:21,
    144:64,
    147:73,
    148:19,
    149:36,
    150:34,
    151:52,
    152:50,
    153:47
    }
    normalized_df = data.copy()
    for image_id, group in normalized_df.groupby('image_id'):
        if image_id in words_per_image_dict:
            word_count = words_per_image_dict[image_id]
            normalized_df.loc[group.index, 'system_time_diff_seconds'] /= word_count
    return normalized_df

def plot_category_matrix_2(data):
    import matplotlib.pyplot as plt
    import pandas as pd
    import numpy as np
    from matplotlib.patches import Polygon

    # Example DataFrame (same as before)
    
    df = create_category_matrix(data)
    # Normalize for colormap
    all_vals = np.array([v for row in df.values for v in row])
    vals1 = all_vals[:,0]
    vals2 = all_vals[:,1]
    vmin = min(vals1.min(), vals2.min())
    vmax = max(vals1.max(), vals2.max())
    cmap = plt.cm.viridis

    fig, ax = plt.subplots(figsize=(6,6))

    n = len(df)
    for i, row in enumerate(df.index):
        for j, col in enumerate(df.columns):
            val1, val2 = df.loc[row, col]
            
            # --- FIX: map row i to bottom-up (no inverted axis) ---
            x0, y0 = j, i
            x1, y1 = j+1, i+1
            
            # Split cell along main diagonal
            tri1 = [(x0,y0),(x1,y0),(x1,y1)]  # bottom-right triangle -> first tuple value
            tri2 = [(x0,y0),(x0,y1),(x1,y1)]  # top-left triangle -> second tuple value
            
            color1 = cmap((val1-vmin)/(vmax-vmin)) if vmax>vmin else (1,1,1,1)
            color2 = cmap((val2-vmin)/(vmax-vmin)) if vmax>vmin else (1,1,1,1)
            
            ax.add_patch(Polygon(tri1, facecolor=color1))
            ax.add_patch(Polygon(tri2, facecolor=color2))
            
            # Optional annotations
            if val1!=0 or val2!=0:
                ax.text(j+0.7, i+0.3, f"{val1:.1f}", ha="center", va="center", fontsize=7)
                ax.text(j+0.3, i+0.7, f"{val2:.1f}", ha="center", va="center", fontsize=7)

    # Ticks/labels
    ax.set_xticks(np.arange(n)+0.5)
    ax.set_yticks(np.arange(n)+0.5)
    ax.set_xticklabels(df.columns)
    ax.set_yticklabels(df.index)  # bottom->top: meme, person, politik, ort

    ax.set_xlim(0,n)
    ax.set_ylim(0,n)
    ax.set_aspect("equal")

    # Colorbar
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=vmin, vmax=vmax))
    cbar = plt.colorbar(sm, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Tuple values")

    plt.show()
#plot_view_duration_images()
#plot_tag_groups(view_duration_df)
#tag_analysis_results = display_tag_group_analysis(view_duration_df)
#visualize_view_time_matrix()
#plot_category_matrix()
#create_category_matrix()
#print("view duration images",view_duration_images(view_duration_df).head())
#plot_category_matrix_2()
#print("view durations",view_duration_df)
#print("Normalisierung:",normalize_view_durations(view_duration_df))

#visualize_view_time_matrix(view_duration_df)
#plot_category_matrix_2(view_duration_df)

#sort the categories with text based on normalized view durations and plot descending

plot_tag_groups(normalize_view_durations(view_duration_df),only_text=True)
visualize_view_time_matrix(view_duration_df)
plot_category_matrix_2(view_duration_df)
# median:
# person politik textimg: 0.47
# ort textimg: 0.55
# person textimg:  0.69
# meme textimg: 0.88
# politik textimg: 0.65
# text: 0.311
# politik_text: 10.400

# mean: