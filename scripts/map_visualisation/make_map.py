import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import geopandas as gpd
import warnings
warnings.filterwarnings('ignore')

# Read the CSV data
url = "../../assembly_mirror_tracker.csv"
df = pd.read_csv(url)

# Get India GeoJSON
geojson_url = "india_bhuvan_states_uts.geojsonl"
gdf = gpd.read_file(geojson_url)

# Create state mapping
state_mapping = {
    'Andhra Pradesh': 'Andhra Pradesh',
    'Arunachal Pradesh': 'Arunachal Pradesh',
    'Assam': 'Assam',
    'Bihar': 'Bihar',
    'Chhattisgarh': 'Chhattisgarh',
    'Goa': 'Goa',
    'Gujarat': 'Gujarat',
    'Haryana': 'Haryana',
    'Himachal Pradesh': 'Himachal Pradesh',
    'Jharkhand': 'Jharkhand',
    'Karnataka': 'Karnataka',
    'Kerala': 'Kerala',
    'Madhya Pradesh': 'Madhya Pradesh',
    'Maharashtra': 'Maharashtra',
    'Manipur': 'Manipur',
    'Meghalaya': 'Meghalaya',
    'Mizoram': 'Mizoram',
    'Nagaland': 'Nagaland',
    'Odisha': 'Odisha',  
    'Punjab': 'Punjab',
    'Rajasthan': 'Rajasthan',
    'Sikkim': 'Sikkim',
    'Tamil Nadu': 'Tamil Nadu',
    'Telangana': 'Telangana',
    'Tripura': 'Tripura',
    'Uttar Pradesh': 'Uttar Pradesh',
    'Uttarakhand': 'Uttarakhand',
    'West Bengal': 'West Bengal',
    'Delhi': 'Delhi',
    'Puducherry': 'Puducherry',
    'Jammu and Kashmir': 'Jammu and Kashmir',
    'Union Territory of Jammu and Kashmir': 'Jammu and Kashmir',
    'Union Territory of Ladakh': 'Ladakh'
}

# Add mapped state names
df['State_Mapped'] = df['State / UT'].map(state_mapping)

# Create status categories
def categorize_status(row):
    asm_status = str(row.get('Assembly Mirror Status', '')).strip()
    council_status = str(row.get('Council Mirror Status', '')).strip()
    
    # Normalize "No sitting council" and empty values
    no_council = ('N/A' in council_status or council_status == '' or 
                  council_status == 'nan' or 'No sitting council' in str(row.get('Council Website', '')))
    
    # Check status types
    asm_completed = 'Completed' in asm_status
    council_completed = 'Completed' in council_status
    asm_needs_update = 'Metadata' in asm_status or 'update' in asm_status.lower()
    council_needs_update = 'Metadata' in council_status or 'update' in council_status.lower()
    asm_in_progress = 'Started' in asm_status or 'pending completion' in asm_status
    council_in_progress = 'Started' in council_status or 'pending completion' in council_status
    
    # Category 1: Both Completed
    if asm_completed and council_completed:
        return 'Both Completed'
    
    # Category 2: Assembly Completed, No Council
    if asm_completed and no_council:
        return 'Assembly Completed'
    
    # Category 3: Assembly Completed, Council In Progress/Needs Update
    if asm_completed and (council_in_progress or council_needs_update):
        return 'Assembly Done, Council Pending'
    
    # Category 4: Both Need Update
    if asm_needs_update and council_needs_update:
        return 'Both Need Update'
    
    # Category 5: Assembly Needs Update only
    if asm_needs_update and no_council:
        return 'Assembly Needs Update'
    
    # Category 6: Council Needs Update only
    if council_needs_update and (asm_completed or not asm_status or asm_status == 'nan'):
        return 'Council Needs Update'
    
    # Category 7: Assembly Needs Update, Council pending
    if asm_needs_update and not no_council:
        return 'Assembly Needs Update (Has Council)'
    
    # Category 8: In Progress (Assembly)
    if asm_in_progress:
        return 'Assembly In Progress'
    
    # Category 9: In Progress (Council)
    if council_in_progress:
        return 'Council In Progress'
    
    # Category 10: No Data
    if not asm_status or asm_status == 'nan':
        return 'No Data'
    
    # Default
    return 'Other'

df['Category'] = df.apply(categorize_status, axis=1)

# Define colors for categories
category_colors = {
    'Both Completed': '#2ca02c',  # Dark green
    'Assembly Completed': '#98df8a',  # Light green
    'Assembly Done, Council Pending': '#74c476',  # Medium green
    'Both Need Update': '#ff7f0e',  # Dark orange
    'Assembly Needs Update': '#ffbb78',  # Light orange
    'Council Needs Update': '#fdd0a2',  # Very light orange
    'Assembly Needs Update (Has Council)': '#fd8d3c',  # Medium orange
    'Assembly In Progress': '#1f77b4',  # Blue
    'Council In Progress': '#6baed6',  # Light blue
    'No Data': '#d3d3d3',  # Gray
    'Other': '#e0e0e0'  # Light gray
}

df['color'] = df['Category'].map(category_colors)

# Merge with geodataframe
gdf = gdf.merge(df, left_on='s_name', right_on='State_Mapped', how='left')
gdf['color'] = gdf['color'].fillna('#f5f5f5')

# Create figure
fig, ax = plt.subplots(1, 1, figsize=(18, 20))

# Plot the map with category colors
gdf.plot(ax=ax, color=gdf['color'], edgecolor='black', linewidth=0.5)

# Get centroids for label positioning
gdf['centroid'] = gdf.geometry.centroid
gdf['x'] = gdf.centroid.x
gdf['y'] = gdf.centroid.y

# Define label positions to avoid intersections
label_positions = {
    'Kerala': (-3.5, -2, 'right'),
    'Tamil Nadu': (3.5, -1,'left'),
    'Karnataka': (-3.5, -0.5, 'right'),
    'Goa': (-4, -1.5, 'right'),
    'Maharashtra': (0, 0, 'center'),
    'Gujarat': (-4, 2, 'right'),
    'Rajasthan': (-3.5, 2, 'right'),
    'Madhya Pradesh': (0, 0, 'center'),
    'Uttar Pradesh': (5, 6, 'left'),
    'Bihar': (0, 0, 'center'),
    'West Bengal': (3, 0, 'left'),
    'Jharkhand': (0, -0.5, 'center'),
    'Orissa': (0, -1.5, 'center'),
    'Chhattisgarh': (0, 0, 'center'),
    'Andhra Pradesh': (3.5, -0.5, 'left'),
    'Telangana': (0, 0, 'center'),
    'Punjab': (-2, 2, 'right'),
    'Haryana': (2.5, 0.5, 'left'),
    'NCT of Delhi': (3, 1, 'left'),
    'Uttarakhand': (0, 1.5, 'center'),
    'Himachal Pradesh': (-2, 2, 'right'),
    'Assam': (0, 0, 'center'),
    'Meghalaya': (3, -1.5, 'left'),
    'Tripura': (3.5, -0.5, 'left'),
    'Mizoram': (3.5, 0.5, 'left'),
    'Manipur': (3.5, 1, 'left'),
    'Nagaland': (3.5, 1.5, 'left'),
    'Arunachal Pradesh': (0, 2, 'center'),
    'Sikkim': (-3, 0.5, 'right'),
    'Puducherry': (3.5, -0.5,'left'),
    'Jammu and Kashmir': (-2, 3, 'right'),
    'Ladakh': (0, 3, 'center')
}

# Add labels for each state
for idx, row in gdf.iterrows():
    if pd.notna(row.get('State / UT')):
        state_name = row['s_name']
        
        # Get label position
        pos = label_positions.get(state_name, (0, 0, 'center'))
        x_offset, y_offset, align = pos
        
        # Create label
        label_parts = []
        
        # Add State/UT name
        if pd.notna(row.get('State / UT')):
            label_parts.append(f"{row['State / UT']}")
        
        # Check if category is "No Data"
        category = row.get('Category', '')
        
        # If No Data, only show state name
        if category == 'No Data':
            label = label_parts[0] if label_parts else ''
        else:
            # Add Category
            if pd.notna(category):
                label_parts.append(f"Status: {category}")
            
            # Add Assembly Mirror Status
            if pd.notna(row.get('Assembly Mirror Status')) and str(row.get('Assembly Mirror Status')).strip():
                asm_status = str(row['Assembly Mirror Status'])
                # Truncate long status messages
                if len(asm_status) > 50:
                    asm_status = asm_status[:47] + '...'
                label_parts.append(f"Assembly: {asm_status}")
            
            # Add Council Mirror Status if available
            council_status = str(row.get('Council Mirror Status', '')).strip()
            if council_status and council_status != 'nan' and 'No sitting council' not in council_status:
                if len(council_status) > 50:
                    council_status = council_status[:47] + '...'
                label_parts.append(f"Council: {council_status}")
            
            # Add Notes if available
            if pd.notna(row.get('Notes')) and str(row.get('Notes')).strip():
                notes = str(row['Notes'])
                if len(notes) > 50:
                    notes = notes[:47] + '...'
                label_parts.append(f"Note: {notes}")
            
            # Join all parts
            label = '\n'.join(label_parts)
        
        # Position the label
        x = row['x'] + x_offset
        y = row['y'] + y_offset
        
        # Add text with background
        ax.annotate(label, xy=(row['x'], row['y']), xytext=(x, y),
                   fontsize=15, ha=align, va='top', wrap=True,
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                            edgecolor='black', alpha=0.95, linewidth=0.7),
                   arrowprops=dict(arrowstyle='-', color='black', lw=0.7, 
                                 connectionstyle='arc3,rad=0.1') if (x_offset != 0 or y_offset != 0) else None,
                   multialignment='left', linespacing=1.3)

# Remove axes
ax.set_axis_off()

# Create legend
legend_elements = [
    mpatches.Patch(facecolor='#2ca02c', edgecolor='black', label='Both Completed'),
    mpatches.Patch(facecolor='#98df8a', edgecolor='black', label='Assembly Completed'),
    mpatches.Patch(facecolor='#74c476', edgecolor='black', label='Assembly Done, Council Pending'),
    mpatches.Patch(facecolor='#ff7f0e', edgecolor='black', label='Both Need Update'),
    mpatches.Patch(facecolor='#fd8d3c', edgecolor='black', label='Assembly Needs Update (Has Council)'),
    mpatches.Patch(facecolor='#ffbb78', edgecolor='black', label='Assembly Needs Update'),
    mpatches.Patch(facecolor='#fdd0a2', edgecolor='black', label='Council Needs Update'),
    mpatches.Patch(facecolor='#1f77b4', edgecolor='black', label='Assembly In Progress'),
    mpatches.Patch(facecolor='#6baed6', edgecolor='black', label='Council In Progress'),
    mpatches.Patch(facecolor='#d3d3d3', edgecolor='black', label='No Data'),
    mpatches.Patch(facecolor='#e0e0e0', edgecolor='black', label='Other')
]

ax.legend(handles=legend_elements, loc='lower center', fontsize=13,
         title='Archive Status Categories', title_fontsize=2, framealpha=0.95,
         ncol=4)

plt.tight_layout()
plt.show()
plt.savefig('status_map.png')

print("\nMap generated successfully!")
print(f"\nAll {len(gdf[gdf['State / UT'].notna()])} states/UTs displayed")
