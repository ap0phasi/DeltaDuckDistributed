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
    num_datasets = len(df.columns)
    colors = generate_color_hex(num_datasets)
    
    chart_json = {
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

    return chart_json

def dataframe_to_table_json(df):
    df = df.reset_index()
    headers = [{"text": col, "value": col.lower().replace(" ", "_")} for col in df.columns]
    items = df.to_dict(orient='records')
    formatted_items = []

    for item in items:
        formatted_item = {k.lower().replace(" ", "_"): v for k, v in item.items()}
        formatted_items.append(formatted_item)

    table_json = {
        "tableData": {
            "headers": headers,
            "items": formatted_items
        }
    }

    return table_json

def create_json_responses(df, response_types):
    combined_json = {
        "respond_to": "duck",
        "response_contents": response_types,
        "data": {}
    }

    if "Chart" in response_types:
        chart_json = dataframe_to_json_chart(df)
        combined_json["data"]["chart"] = chart_json["chartData"]

    if "Table" in response_types:
        table_json = dataframe_to_table_json(df)
        combined_json["data"]["table"] = table_json["tableData"]

    return combined_json

if __name__=="__main__":
   # Example usage
    data = {
        "Data One": [40, 39, 10, 40, 39, 80, 40],
        "Data Two": [23, 13, 61, 35, 12, 23, 45]
    }
    index = ['January', 'February', 'March', 'April', 'May', 'June', 'July']
    df = pd.DataFrame(data, index=index)

    json_output = create_json_responses(df, ["Chart","Table"])
    print(json_output)