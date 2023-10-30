import pandas as pd
import json
import colorsys

def generate_color_hex(num_colors):
    colors = []
    for i in range(num_colors):
        hue = i / num_colors
        lightness = 0.5
        saturation = 0.9
        rgb = colorsys.hls_to_rgb(hue, lightness, saturation)
        hex_color = "#{:02x}{:02x}{:02x}".format(int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
        colors.append(hex_color)
    return colors

def dataframe_to_json_chart(df):
    # Determine number of required colors
    num_datasets = len(df.columns)
    colors = generate_color_hex(num_datasets)
    
    # Convert DataFrame to the required JSON format
    chart_json = {
        "respond_to": "duck",
        "response_contents": ["chart"],
        "chartData": {
            "labels": list(df.index),
            "datasets": []
        }
    }

    for i, column in enumerate(df.columns):
        dataset = {
            "label": column,
            "backgroundColor": colors[i % len(colors)],
            "borderColor": colors[i % len(colors)],
            "tension": 0.2,
            "data": df[column].tolist()
        }
        chart_json["chartData"]["datasets"].append(dataset)

    return json.dumps(chart_json, indent=4)

if __name__=="__main__":
   # Example usage
    data = {
        "Data One": [40, 39, 10, 40, 39, 80, 40],
        "Data Two": [23, 13, 61, 35, 12, 23, 45]
    }
    index = ['January', 'February', 'March', 'April', 'May', 'June', 'July']
    df = pd.DataFrame(data, index=index)

    json_output = dataframe_to_json_chart(df)
    print(json_output)