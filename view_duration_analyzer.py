#aggregates view duration data
# measures view duration for stimuli and participants
# analyzes view duration patterns for grouped data
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from lifelines import WeibullAFTFitter
from lifelines import LogNormalAFTFitter

view_duration_df = pd.read_csv('view_durations.csv')
words_per_image_dict = {
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
    128:19,
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

def create_textimg_df(data, drop_non_text=True):
    #create a dataframe with all images that appear in words_per_image_dict, their number of words, their median system time diff as "duration" and their tagstring as "category"
    textimg_data = []
    for image_id, group in data.groupby('image_id'):

        if image_id in words_per_image_dict:
            word_count = words_per_image_dict[image_id]
        elif not drop_non_text:
            word_count = 0
        elif drop_non_text:
            continue
        median_duration = group['system_time_diff_seconds'].median()
        #get the tagstring from any of the image names in the group
        tagstring = group.iloc[0]['image_name'].split('_')[1:-1]
        for tag in tagstring.copy():
            if tag == "ncc":
                tagstring.remove("ncc")
            elif tag =="textigm" or tag == "textimg":
                tagstring.remove(tag)
                tagstring.append("text")
        print("tagstring: ",tagstring, "image id: ",image_id)
        tagstring = '_'.join(tagstring)
        textimg_data.append({
            'image_id': image_id,
            'words': word_count,
            'duration': median_duration,
            'category': tagstring
        })

    return pd.DataFrame(textimg_data)

def create_image_tag_dict(data,new_labels=False):
    if new_labels:
        return adjust_categories(data).set_index('image_id')['tag_combination'].to_dict()
    else:
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

def analyze_tag_groups(data, only_text=False, new_labels=False):
    # Create a dictionary to group images by their tag combinations
    tag_group_dict = {}
    
    # Group images by their tag combinations
    for image_id, tags in create_image_tag_dict(data, new_labels).items():
        tag_combination = tuple(sorted(tags))  # Use sorted tuple for consistent grouping
        if tag_combination not in tag_group_dict:
            tag_group_dict[tag_combination] = []
        
        if not only_text:
            tag_group_dict[tag_combination].append(image_id)
        else:
            try:
                # triggers if image id is in words per image dict, therefore has text
                tags = words_per_image_dict[image_id]
                tag_group_dict[tag_combination].append(image_id)
            except KeyError:
                continue
        #if (only_text and words_per_image_dict[image_id] is not None) or not only_text:
            
        
    
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
def display_tag_group_analysis(data,only_text=False,new_labels=False):
    tag_analysis = analyze_tag_groups(data,only_text,new_labels)
    
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
def plot_tag_groups(data,only_text = False,new_labels=False):
    tag_analysis = analyze_tag_groups(data,only_text,new_labels)
    
    if new_labels == False:
        #bandaid solution for dropping falsely labeled data
    
        #tag_analysis = tag_analysis.drop([1,2])
    
        #frag nicht mich wieso die Indizes so sind
        pass
    #drop rows where the tag_string is one of the following: textimg, meme_textigm [sic]
    print("TAG ANALYSIS ",tag_analysis)
    
    tag_analysis = tag_analysis[~tag_analysis['tag_string'].isin(['textimg', 'meme_textigm'])]

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

def create_view_time_matrix(data,only_text=False,new_labels=False):
    # Create a matrix with semantic categories on the one axis and text/no-text on the other axis
    # images with text are marked with the tag textimg, images with text only are marked with the tag text
    if new_labels:
        semantic_categories = ["meme", "person", "politik", "ort","meme_politik","person_politik","meme_person_politik"]
    else:
        semantic_categories = ["meme", "person", "politik", "ort","person_politik"]
    tag_analysis_df = analyze_tag_groups(data,only_text,new_labels)

    # Create the view time matrix
    view_time_matrix = pd.DataFrame(0, index=semantic_categories, columns=["text", "no_text"], dtype=int)
    print("tag analysis",tag_analysis_df)
    # for every tag combination in tag_analysis_df["tag_combination"]

    for idx, row in tag_analysis_df.iterrows():
        if 'text' == row['tag_string']:
            view_time_matrix.at["Nur Text", "text"] = row['median_system_time']
            continue
        for category in semantic_categories:
            #if category in row['tag_string']
            if row['tag_string'] in [category, category+"_text", category+"_textimg"]:
                # note that textigm is a misspelled version of textimg
                if 'text' in row['tag_string'] and not 'textigm' in row['tag_string']:
                    view_time_matrix.at[category, "text"] = row['median_system_time']
                elif 'textigm' in row['tag_string']:
                    #misspelled file name
                    pass
                else:
                    view_time_matrix.at[category, "no_text"] = row['median_system_time']
        

    return view_time_matrix

def visualize_view_time_matrix(data,new_labels=False):
    view_time_matrix = create_view_time_matrix(data,new_labels=new_labels)
    plt.figure(figsize=(10, 6))
    mask = view_time_matrix == 0
    sns.heatmap(view_time_matrix, mask = mask ,annot=True, cmap="YlGnBu", cbar_kws={'label': 'Median der Betrachtungsdauer in Sekunden'})
    plt.title("Matrix Betrachtungsdauer")
    plt.xlabel("Präsez von Text")
    plt.ylabel("Kategorien")
    plt.show()
def create_category_matrix(data,only_text=False,new_labels=False):
    semantic_categories = ["meme", "person", "politik", "ort"]
    tag_analysis_df = analyze_tag_groups(data,only_text,new_labels)
    #NxN matrix with each semantic category on both axes. 
    # Each cell shows the average system time diff for the combined category n,m without text
    category_matrix = pd.DataFrame(0, index=semantic_categories, columns=semantic_categories, dtype=float)
        
    print(category_matrix)
    for idx, row in tag_analysis_df.iterrows():
        for category in semantic_categories:
            for other_category in semantic_categories:
                cell = category_matrix.at[category, other_category]
                #if other_category in row['tag_string'] and category in row['tag_string']:
                if(len(row['tag_combination'])>=3):
                    print("ALARM")
                if (category in row['tag_string'] and other_category in row['tag_string']) and (len(row['tag_combination'])<3 or "text" in row['tag_string'] and len(row['tag_combination'])<4):
                    
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
def adjust_categories(data):
    modified_labels_dict = {}
    modified_labels_dict = {0: ['meme'], 1: ['meme'], 2: ['meme'], 3: ['meme'], 4: ['meme'], 5: ['meme'], 6: ['meme'], 7: ['meme'], 8: ['meme'], 9: ['meme'], 10: ['meme'], 11: ['ort', 'text'], 12: ['ort', 'text'], 13: ['ort', 'text'], 14: ['ort'], 15: ['ort', 'text'], 16: ['ort', 'text'], 17: ['ort', 'text'], 18: ['ort'], 19: ['ort'], 20: ['ort'], 21: ['ort'], 22: ['ort'], 23: ['ort'], 24: ['ort'], 25: ['ort'], 26: ['ort'], 27: ['ort'], 28: ['ort'], 29: ['ort'], 30: ['ort'], 31: ['ort'], 32: ['ort'], 33: ['person', 'text'], 34: ['person', 'text'], 35: ['person'], 36: ['person'], 37: ['person'], 38: ['person'], 39: ['person'], 40: ['person'], 41: ['person'], 42: ['person'], 43: ['person'], 44: ['person'], 45: ['person'], 46: ['person'], 47: ['person'], 48: ['person'], 49: ['person'], 50: ['person'], 51: ['person'], 52: ['person'], 53: ['person'], 54: ['person'], 55: ['person'], 56: ['person'], 57: ['person'], 58: ['person'], 59: ['person'], 60: ['person'], 61: ['person'], 62: ['person'], 63: ['person'], 64: ['person'], 65: ['person'], 66: ['person'], 67: ['person'], 68: ['person'], 69: ['person'], 70: ['person'], 71: ['person'], 72: ['person'], 73: ['person'], 74: ['person', 'text'], 75: ['person'], 76: ['person', 'text'], 77: ['person'], 78: ['person'], 79: ['person'], 80: ['person'], 81: ['person'], 82: ['person', 'text'], 83: ['person'], 84: ['person', 'text'], 85: ['person', 'text'], 86: ['person'], 87: ['person', 'text'], 88: ['person', 'text', 'politik'], 89: ['person', 'politik'], 90: ['person', 'politik'], 91: ['person', 'politik'], 92: ['person', 'politik', 'text'], 93: ['person', 'politik'], 94: ['person', 'politik'], 95: ['person', 'politik'], 96: ['person', 'politik'], 97: ['person', 'politik'], 98: ['person', 'politik'], 99: ['person', 'politik', 'text'], 100: ['person', 'politik', 'text'], 101: ['person', 'politik'], 102: ['person', 'politik', 'text'], 103: ['politik', 'person'], 104: ['politik', 'person'], 105: ['politik', 'person'], 106: ['meme', 'text', 'politik'], 107: ['politik', 'person', 'text', 'meme'], 108: ['meme', 'text'], 109: ['meme', 'text', 'politik'], 110: ['meme', 'text'], 111: ['meme', 'text'], 112: ['meme', 'text'], 113: ['meme', 'text'], 114: ['meme', 'text'], 115: ['meme', 'text'], 116: ['meme', 'text', 'politik'], 117: ['meme', 'text', 'politik'], 118: ['meme', 'text'], 119: ['meme', 'text'], 120: ['meme', 'text'], 121: ['meme', 'text'], 122: ['meme', 'text', 'politik'], 123: ['meme', 'text', 'politik'], 124: ['meme', 'text', 'politik'], 125: ['text', 'meme'], 126: ['text', 'politik'], 127: ['text', 'politik'], 128: ['text', 'ort'], 129: ['text', 'ort'], 130: ['text', 'ort'], 131: ['text', 'person', 'politik'], 132: ['text', 'person'], 133: ['text', 'person'], 134: ['text', 'politik', 'person'], 135: ['text', 'person', 'politik', 'meme'], 136: ['text', 'person', 'politik'], 137: ['text', 'person', 'politik'], 138: ['text', 'person', 'politik'], 139: ['text', 'person', 'politik'], 140: ['text', 'person', 'politik'], 141: ['text', 'meme', 'politik'], 142: ['text'], 143: ['text'], 144: ['text'], 145: ['text'], 146: ['text', 'politik'], 147: ['text', 'meme'], 148: ['text', 'meme'], 149: ['text', 'meme'], 150: ['text', 'meme'], 151: ['text', 'meme', 'politik'], 152: ['text', 'meme', 'politik'], 153: ['text', 'meme', 'politik']}
    modified_df = data.copy()
    modified_df['tag_combination'] = modified_df['image_id'].map(modified_labels_dict)
    print("modified:",modified_df,"original:",data)
    return modified_df
def normalize_view_durations(data):
    # divide system time diff by the number of words as seen in words_per_image_dict on each image where the id is present in words_per_image_dict.
    method = "division_after_min_time_substraction"

    normalized_df = data.copy()
    for image_id, group in normalized_df.groupby('image_id'):
        if image_id in words_per_image_dict:
            word_count = words_per_image_dict[image_id]

            if method == "division":
                normalized_df.loc[group.index, 'system_time_diff_seconds'] /= word_count
            elif method == "distance_to_median":
                median = 8.669335
                pass
            elif method == "division_after_min_time_substraction":
                median = 8.669335
                normalized_df.loc[group.index, 'system_time_diff_seconds'] = (normalized_df.loc[group.index, 'system_time_diff_seconds'] - 5) / word_count
                # set every nevative value to 0
                normalized_df.loc[group.index, 'system_time_diff_seconds'] = normalized_df.loc[group.index, 'system_time_diff_seconds'].apply(lambda x: max(x, 0))
    return normalized_df

def plot_category_matrix_2(data):
    import matplotlib.pyplot as plt
    import pandas as pd
    import numpy as np
    from matplotlib.patches import Polygon

    # Example DataFrame (same as before)
    
    df = create_category_matrix(data)
    # Normalize for colormap
    print(df.values)
    all_vals = np.array([v for row in df.values for v in row])
    print(all_vals)
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

def tobit_regression(data):
    
    import pandas as pd
    import statsmodels.formula.api as smf
    from statsmodels.miscmodels.ordinal_model import OrderedModel
    from statsmodels.duration.hazard_regression import PHReg
    import statsmodels.api as sm
    from statsmodels.discrete.discrete_model import Tobit
    
    # Example data
    df = data
    # Lower and upper censoring points
    low, high = 5.0, 15.0

    # Tobit regression with censoring
    model = Tobit(df["duration"], sm.add_constant(pd.get_dummies(df[["words", "category"]], drop_first=True)),
                left=low, right=high)
    res = model.fit()
    print(res.summary())

def fit_aft(df, duration_col="duration", words_col="words", category_col="category"):
    """
    Fit a Weibull AFT model where each subcategory from a compound category string
    is treated as its own predictor (multi-hot encoding).
    
    Args:
        df: DataFrame with duration, words, category.
        duration_col: Column with viewing times.
        words_col: Column with word counts.
        category_col: Column with compound category strings (e.g. 'person_politik_text').
    """
    data = df.copy()

    # Define censoring: if exactly at lower/upper bound, treat as censored
    data["event_observed"] = ~data[duration_col].isin([5.0, 15.0])

    # Split categories into multiple binary indicators
    # e.g. "person_politik_text" → {"person":1, "politik":1, "text":1}
    dummies = data[category_col].str.get_dummies(sep="_")

    # Combine predictors: words + dummies
    X = pd.concat([data[[duration_col, words_col, "event_observed"]], dummies], axis=1)

    # Fit Weibull AFT
    aft = WeibullAFTFitter()
    aft.fit(X, duration_col=duration_col, event_col="event_observed")
    
    aft.print_summary()
    return aft, X

def censored_regression(data):
    import pandas as pd
    from lifelines import WeibullAFTFitter
    
    # Example dataset: durations bounded between 5 and 15
    df = data

    # 1. Define censoring
    # If duration = 5 or 15 → censored (lower or upper bound)
    df["event_observed"] = ~df["duration"].isin([5.0, 15.0])  

    # 2. Convert categorical variable into dummies
    df = pd.get_dummies(df, columns=["category"], drop_first=True)

    # 3. Fit Weibull AFT model
    aft = WeibullAFTFitter()
    aft.fit(df, duration_col="duration", event_col="event_observed")

    # 4. Show results
    aft.print_summary()
    aft.plot()

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

#plot_tag_groups(view_duration_df)
#plot_tag_groups(normalize_view_durations(view_duration_df),only_text=True)
#visualize_view_time_matrix(view_duration_df)
#plot_category_matrix_2(view_duration_df)

# median:
# person politik textimg: 0.47
# ort textimg: 0.55
# person textimg:  0.69
# meme textimg: 0.88
# politik textimg: 0.65
# text: 0.311
# politik_text: 10.400

# mean:

#print("img text dict",create_textimg_df(view_duration_df))

#print("="*30+"\nNEUE LABELS\n\n"+"="*30)
#print(display_tag_group_analysis(normalize_view_durations(view_duration_df),only_text=False,new_labels=True))
#print("="*30+"\nALTE LABELS\n\n"+"="*30)
#print(display_tag_group_analysis(normalize_view_durations(view_duration_df),only_text=False,new_labels=False))

#plot_tag_groups(view_duration_df,new_labels=False)
#plot_tag_groups(normalize_view_durations(view_duration_df),only_text=True,new_labels=True)
#plot_tag_groups(normalize_view_durations(view_duration_df),only_text=True,new_labels=False)

#analyze_tag_groups(normalize_view_durations(view_duration_df),only_text=True,new_labels=True)
#analyze_tag_groups(normalize_view_durations(view_duration_df),only_text=True,new_labels=False)

#display_tag_group_analysis(normalize_view_durations(view_duration_df),only_text=True,new_labels=True)
#visualize_view_time_matrix(view_duration_df,new_labels=False)
#visualize_view_time_matrix(view_duration_df,new_labels=False)
#plot_category_matrix_2(view_duration_df)

#tobit_regression(view_duration_df)
#censored_regression(create_textimg_df(adjust_categories(view_duration_df)))
#print(analyze_tag_groups(view_duration_df, new_labels=False))
#print(create_textimg_df(view_duration_df))
#fit_aft(create_textimg_df(view_duration_df, drop_non_text=False))
#display_tag_group_analysis(view_duration_df,only_text=False,new_labels=False)
#plot_category_matrix_2(view_duration_df)
