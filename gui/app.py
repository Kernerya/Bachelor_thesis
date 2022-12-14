import json
from typing import List
import dash
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import pandas as pd
from dash import Input, Output, State, dcc, html
import plotly.graph_objs as go

# Colors
bgcolor = "#f3f3f1"  # mapbox light map land color
bar_bgcolor = "#b0bec5"  # material blue-gray 200
bar_unselected_color = "#78909c"  # material blue-gray 400
bar_color = "#546e7a"  # material blue-gray 600
bar_selected_color = "#37474f"  # material blue-gray 800
bar_unselected_opacity = 0.8

# Styles
OPTIONS_CONTAINER = {
    "alignItems": "baseline",
    "display": "none"
}

OPTIONS_STYLE = {
    "borderRadius": "10px",
    "border": "2px solid #A2C2C2",
    "width": "30%",
    "padding": "5px",
    "margin": "5px",
}

NETWORK_STYLE = {
    "width": "100%",
    "height": "100%",
    "backgroundColor": "linear-gradient(rgba(255, 255, 255, 1), rgba(118, 118, 118, 1))",
}

NETWORK_STYLESHEET = [
    {
        'selector': 'node',
        'style': {
            'content': 'data(label)',
            'backgroundColor': "black",
            'width': "10px",
            'height': "10px",
        }
    },
    {
        'selector': '.LinkWanDown',
        'style': {
            'width': "8px",
            'height': "8px",
            'label': 'WAN'
        }
    },
    {
        'selector': '.LinkEthernet',
        'style': {
            'width': "8px",
            'height': "8px",
            'line-color': "#ABE8E8",
            'label': 'Ethernet'
        }
    },
    {
        'selector': '.LinkWifiBetweenTrafficLights',
        'style': {
            'width': "8px",
            'height': "8px",
            'line-color': "#ffffff",
            'label': 'WiFi'
        }
    },
    {
        'selector': '.LinkWifiTaxiToTrafficLight',
        'style': {
            'width': "8px",
            'height': "8px",
            'line-color': "#6d8f8f",
            'label': 'Wifi'
        }
    },
    {
        'selector': '.taxi',
        'style': {
            "background-image": ["./assets/2.png"],
            'background-fit': 'cover',
            "width": "50px",
            "height": "50px"
        }
    },
    {
        'selector': '.traffic',
        'style': {
            "background-image": ["./assets/1.png"],
            'background-fit': 'cover',
            "width": "50px",
            "height": "50px"
        }
    },

]

NODEPANEL_STYLE = {
    "position": "absolute",
    "right": "-50%",
    "height": "100vh",
    "width": "50%",
    "transition": "all 1000ms",
    "backgroundColor": "#A2C2C2",
    "zIndex": "10000",
    "color": "white",
    "padding": "25px",
    "overflowY": "scroll"
}

SELECT_STYLE = {
    "padding": "3px",
    "width": "100px",
    "margin": "3px",
    "backgroundColor": "#A2C2C2",
    "borderRadius": "20px",
    "border": "3px #A2C2C2 solid",
    "color": "white",
    "marginRight": "15px",
    "marginLeft": "5px"
}

DESELECT_STYLE = {
    "display": "none",
    "padding": "3px",
    "width": "100px",
    "margin": "5px",
    "backgroundColor": "#A2C2C2",
    "marginLeft": "5px",
    "marginRight": "15px",
    "position": "relative",
    "zIndex": "2",
    "borderRadius": "50px",
    "border": "3px #A2C2C2 solid",
    "color": "white",
}

OVERLAY_STYLE = {
    "position": "fixed",
    "width": "100vw",
    "height": "100vh",
    "display": "none",
    "top": "0",
    "left": "0",
    "right": "0",
    "bottom": "0",
    "backgroundColor": "rgba(0,0,0,0.5)",
    "zIndex": "1"
}

NODE_NAMES_STYLE = {
    "fontFamiliy": "Avenir",
    "filter": "drop-shadow(5px 5px 5px #808080)",
    "margin": "5px",
    "color": "white",
    "fontSize": "larger",
    "padding": "8px",
    "borderBottom": "1.5px white solid",
    "marginBottom": "15px",
    "justifyContent": "center"
}

CHART_STYLE = {
    "borderRadius": "10px",
    "background": "white",
    "padding": "6px",
    "margin": "5px",
    "fontFamiliy": "Avenir",
    "filter": "drop-shadow(5px 5px 5px #879696)",
}

SUM_CHART_STYLE = {
    "display": "none",
    "borderRadius": "10px",
    "background": "white",
    "padding": "6px",
    "margin": "5px",
    "fontFamiliy": "Avenir",
    "filter": "drop-shadow(5px 5px 5px #879696)",
}

SUM_CHART_LINKS_STYLE = {
    "display": "none",
    "borderRadius": "10px",
    "background": "white",
    "padding": "6px",
    "margin": "5px",
    "fontFamiliy": "Avenir",
    "filter": "drop-shadow(5px 5px 5px #879696)",
}

SUM_PLOT_CONTAINER = {
    "display": "none",
    "borderRadius": "10px",
    "background": "white",
    "padding": "5px",
    "margin": "5px",
    "fontFamiliy": "Avenir",
    "filter": "drop-shadow(5px 5px 5px #879696)",
}

CHECKBOXES_CONTAINER_STYLE = {
    "marginLeft": "4px"
}

template = {
    "layout":
        {
            "paper_bgcolor": bgcolor,
            "plot_bgcolor": bgcolor
        }
}


def load_data(basedir):
    """This can be replaced by real-time simulation code at some point"""
    with open(f"{basedir}/config.json", "r") as f:
        config = json.load(f)
    with open(f"{basedir}/infrastructure.json", "r") as f:
        infrastructure = json.load(f)
    node_measurements = pd.read_csv(f"{basedir}/node_measurements.csv")
    link_measurements = pd.read_csv(f"{basedir}/link_measurements.csv")
    return config, infrastructure, node_measurements, link_measurements


def infrastructure_to_cyto_dict(infrastructure):
    elements = []
    position = {}
    for node in infrastructure["nodes"]:
        if "x" in node and "y" in node:
            position = {'x': node["x"], 'y': node["y"]}
        else:
            position = {'x': 0, 'y': 0}

        elements.append({
            'data': {'id': node["id"], 'label': node["id"]},
            'position': position,
            'classes': set_type_of_node(node['id']),
            'selectable': node["id"] in get_selectable_nodes()
        }
        )
    for link in infrastructure["links"]:
        src, dst = link["id"].split("$")
        elements.append({
            'data': {'source': src, 'target': dst, "id": link["id"]},
            'position': position,
            'classes': link['class'],

        })
    return elements


def blank_fig(height):
    """
    Build blank figure with the requested height
    """
    return {
        "data": [],
        "layout": {
            "height": height,
            "template": template,
            "xaxis": {"visible": False},
            "yaxis": {"visible": False},
        },
    }


df_nodes = [pd.DataFrame()]
df_edges = [pd.DataFrame()]


# chart for energy consumption
def power_fig(measurements, node_ids: List[str], is_nodes=True):
    if is_nodes:
        if df_nodes[0].empty:
            df = measurements.pivot_table(index='time', columns='id', values=["static_power", "dynamic_power"])
            df.columns = df.columns.swaplevel()
            df_nodes[0] = df
        else:
            df = df_nodes[0]
    else:
        if df_edges[0].empty:
            df = measurements.pivot_table(index='time', columns='id', values=["static_power", "dynamic_power"])
            df.columns = df.columns.swaplevel()
            df_edges[0] = df
        else:
            df = df_edges[0]

    fig = go.Figure()
    for node_id in node_ids:
        node_df = df[node_id]
        fig.add_trace(
            go.Scatter(x=node_df.index, y=node_df["static_power"], name=node_id + " Static power", line_width=1))
        fig.add_trace(
            go.Scatter(x=node_df.index, y=node_df["dynamic_power"], name=node_id + " Dynamic power", line_width=1))

    fig.update_layout(
        title=f"Power usage: {', '.join(node_ids)}",
        xaxis_title="Time in sec",
        yaxis_title="Power usage (Watt)",
        font_family="Avenir",
        font_color="black",

        legend=dict(
            x=1,
            y=1,
            traceorder="normal",

        ),
        plot_bgcolor='#e5ecf6',
    )
    fig.update_xaxes(showline=True, linewidth=1, linecolor='white', gridcolor='white')
    fig.update_yaxes(showline=True, linewidth=1, linecolor='white', gridcolor='white')

    return fig


# chart for sum of energy consumption
def sum_power_fig(measurements, node_ids: List[str]):
    df = pd.DataFrame(measurements, columns=["time", "id", "static_power", "dynamic_power"])
    df = df[df["id"].isin(node_ids)].groupby("time").sum()
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df.index, y=df["static_power"], name="Sum Static power", line_width=1))
    fig.add_trace(go.Scatter(x=df.index, y=df["dynamic_power"], name="Sum Dynamic power", line_width=1))

    fig.update_layout(
        title=f"Summed power usage:  {', '.join(node_ids[0:3])}" + "..." if len(
            node_ids) > 3 else f"Summed power usage:  {', '.join(node_ids)}",
        xaxis_title="Time in sec",
        yaxis_title="Summed power usage (Watt)",
        font_family="Avenir",
        font_color="black",
        legend=dict(
            x=1,
            y=1,
            traceorder="normal",
        ),
        plot_bgcolor='#f6f6e5',
    )
    fig.update_xaxes(showline=True, linewidth=1, linecolor='white', gridcolor='white')
    fig.update_yaxes(showline=True, linewidth=1, linecolor='white', gridcolor='white')

    return fig


def set_type_of_node(nodeid):
    node_type = nodeid.lower()
    if nodeid.startswith("taxi"):
        node_type = "taxi"
    elif nodeid.startswith("traffic"):
        node_type = "traffic"

    return node_type


def get_selectable_nodes():
    helper_list = []
    for elem in node_measurements["id"]:
        helper_list.append(elem)
    return list(dict.fromkeys(helper_list))


def get_selectable_links():
    helper_list = []
    for elem in link_measurements["id"]:
        helper_list.append(elem)
    return list(dict.fromkeys(helper_list))


def select_all(list):
    for elem in list:
        NETWORK_STYLESHEET.append({
            "selector": "." + elem,
            "style": {
                "backgroundColor": "#ABE8E8",
                'content': 'data(label)',
                'width': "100px",
                'height': "100px",
            }
        })


# update style after selection of nodes
def highlight_selectable_nodes():
    for nodeID in get_selectable_nodes():
        NETWORK_STYLESHEET.append({
            "selector": "." + nodeID,
            "style": {
                "backgroundColor": "#ABE8E8",
                'content': 'data(label)',
                'width': "100px",
                'height': "100px",
            }
        })


config, infrastructure, node_measurements, link_measurements = load_data(
    "../examples/smart_city_traffic/vis_results/fog_2")
timeseries_chart = dcc.Graph(
    config={"displayModeBar": True},
    style=CHART_STYLE,
    figure={}
)
sum_chart = dcc.Graph(
    config={"displayModeBar": True},
    style=SUM_CHART_STYLE,
    figure={}
)

sum_chart_links = dcc.Graph(
    config={"displayModeBar": True},
    style=SUM_CHART_LINKS_STYLE,
    figure={}
)


def main():
    # https://dash.plotly.com/cytoscape/reference
    highlight_selectable_nodes()
    options_list = ["select all"]

    for i in get_selectable_nodes():
        if i not in options_list:
            options_list.append(i)

    options = [{'label': i, 'value': i} for i in options_list]

    options_checklist_list = []
    for j in infrastructure["100"]["nodes"]:
        if j["class"] not in options_checklist_list:
            options_checklist_list.append(j["class"])
    options_checklist = [{'label': s, 'value': set_type_of_node(s)} for s in options_checklist_list]

    network = cyto.Cytoscape(
        layout={
            'name': 'breadthfirst'
        },
        elements=infrastructure_to_cyto_dict(infrastructure["100"]),
        style=NETWORK_STYLE,
        #Set the min and max zoom
        #maxZoom=10,
        #minZoom=0.1,
        stylesheet=NETWORK_STYLESHEET,
        id="network"

    )
    app = dash.Dash(title='leaf-gui', update_title='Loading...', external_stylesheets=[dbc.themes.BOOTSTRAP])

    search_button = html.Button('Search', id='submit-val', n_clicks=0,
                                style={
                                    "borderStyle": "none",
                                    "backgroundColor": "transparent",
                                    "color": "#a2c2c2"
                                })

    search_node_types = html.Div(children=[dcc.Input(
        id="input",
        type="text",
        value="",
        placeholder=" search for node types..",
        style={
            "width": "90%",
            "zIndex": "10",
            "height": "36px",
            "borderRadius": "5px",
            "marginLeft": "7px",
            "borderStyle": "none",
            "backgroundColor": "transparent"
        }
    ), search_button], style=OPTIONS_STYLE, id="search-node-types")

    search_node_ids = html.Div(dcc.Dropdown(
        placeholder="select specific node id",
        options=options,
        value=[""],
        multi=True,
        id='dd_input',
        style={"borderStyle": "none", "backgroundColor": "transparent"},
    ), style=OPTIONS_STYLE)

    select_all_btn = html.Button(children=['Select all'], id="select", className="selectButton", n_clicks=0,
                                 style=SELECT_STYLE)
    deselect_all_btn = html.Button(children=['Deselect all'], id="deselect", className="deselectButton", n_clicks=0,
                                   style=DESELECT_STYLE)

    first_infrastructure_time = int(list(infrastructure)[0])
    last_infrastructure_time = int(list(infrastructure)[len(list(infrastructure)) - 1])

    counter = 0
    time_marks = {}
    for time in infrastructure:
        if counter == 0 or counter % 40 == 0 or counter == len(list(infrastructure)) - 1:
            time_marks[time] = {
                "label": time,
                'style': {'color': '#f50'}
            }
        else:
            time_marks[time] = {
                "label": "",
            }
        counter += 1

    filter_options = html.Div(
        dbc.Row([

            html.Div([
                html.Div(dcc.Dropdown(
                    id='dpdn',
                    value='breadthfirst',
                    placeholder="Choose preferred network layout",
                    clearable=False,
                    options=[
                        {'label': name.capitalize(), 'value': name}
                        for name in ['preset', 'breadthfirst', 'grid', 'random', 'circle', 'cose', 'concentric']
                    ]
                ),
                style=OPTIONS_STYLE),
                html.Div(id='output')
            ], style={"marginLeft": "0px"}),
            html.H6("check the node types which should be displayed on the network:",
                    style={"marginLeft": "4px", "padding": "20px"}),
            html.Div(id="checkboxes_container", children=[dcc.Checklist(id="checkboxes", options=options_checklist)],
                     style=CHECKBOXES_CONTAINER_STYLE),
            html.H6("choose a timeslot that should be displayed on the network:",
                    style={"marginLeft": "4px", "padding": "20px"}),
            html.Div(dcc.Slider(first_infrastructure_time, last_infrastructure_time, 100,
                                value=100, id="slider", marks=time_marks), style={"paddingLeft": "15px"}),
            html.Div(id="slider-value", style={"marginLeft": "4px", "padding": "20px", "marginTop": "-20px"}),

        ], id="options_container", style=OPTIONS_CONTAINER
        ), style={"display": "list-item"}
    )
    filter_icon = dbc.Col(style={"padding": "10px"}, children=[html.Div(id="filter", className="close", n_clicks=0,
                                                                        children=[html.Span(id="line_1"),
                                                                                  html.Span(id="line_2"),
                                                                                  html.Span(id="line_3")])])

    node_panel = html.Div(children=[
        dbc.Row(
            timeseries_chart, className='plotContainer', id="test"

        )
    ], style=NODEPANEL_STYLE, id="nodepanelID")

    overlay = html.Div(id="overlay", style=OVERLAY_STYLE)
    app.layout = html.Div([
        overlay,
        node_panel,
        html.Div(children=[filter_icon, filter_options, search_node_types,
                           html.Div(id='container-button-basic', children=''), search_node_ids, select_all_btn,
                           deselect_all_btn], id="header",
                 style={"backgroundColor": "white", "display": "block", "justifyContent": "space-between",
                        "position": "absolute", "width": "100vw", "zIndex": "10"}),
        dbc.Row([
            dbc.Col(html.Div(network, className='networkContainer')),
        ], className='childrenContainer', id="networkID"),
        sum_chart,
        sum_chart_links

    ], style={"overflow": "hidden"}, id="applayoutID")

    last_plot: [] = [[]]

    # check if nodes are selectable  (legal)
    def are_nodes_selectable(selectednodedata):
        all_selectable = True
        legal_nodes_list = []
        for node in selectednodedata:
            # node is not legal
            if not node["id"] in get_selectable_nodes():
                # the legal list remains empty
                all_selectable = False
            # node is legal
            else:
                # list is filled with legal nodes
                legal_nodes_list.append(node)

        return all_selectable, legal_nodes_list

    def close_node_panel():
        NODEPANEL_STYLE["right"] = "-50%"

    def open_node_panel():
        NODEPANEL_STYLE["right"] = "0"

    def is_node_panel_open():
        right = NODEPANEL_STYLE["right"]
        if right == "-50%":
            return False
        elif right == "0":
            return True

    selected_nodes_backup: [] = []

    def reset_dash_nodes():
        for nodeID in selected_nodes_backup:
            for elem in NETWORK_STYLESHEET:
                if elem["selector"] == "." + nodeID:
                    elem["style"]["backgroundColor"] = "#ABE8E8"
                    elem["style"]["content"] = 'data(label)'
                    elem["style"]["width"] = '100px'
                    elem["style"]["height"] = '100px'
        for nodeID in selected_nodes_backup:
            selected_nodes_backup.remove(nodeID)

    def set_selected_nodes(selected_node_data):
        is_first_call = True
        for nodeID in selected_node_data:
            selected_nodes_backup.append(nodeID)
            is_first_call = True
            for el in NETWORK_STYLESHEET:
                if el["selector"] == "." + nodeID:
                    is_first_call = False
                    el["style"]["backgroundColor"] = "#A2C2C2"
                    el["style"]["content"] = 'data(label)'
                    el["style"]["width"] = '100px'
                    el["style"]["height"] = '100px'

        if selected_node_data and is_first_call:
            NETWORK_STYLESHEET.append({
                "selector": "." + nodeID,
                "style": {
                    "backgroundColor": "#A2C2C2",
                    'content': 'data(label)',
                    'width': "100px",
                    'height': "100px",
                }
            })

    def show_element(style, show):
        show_str = "none"
        if show:
            show_str = "block"
        style["display"] = show_str

    def button_clicked(click_backup, is_select):
        click_backup[0] += 1
        reset_dash_nodes()
        NODEPANEL_STYLE["width"] = "75%"
        if is_select:
            open_node_panel()
            show_element(OVERLAY_STYLE, True)
            set_selected_nodes(get_selectable_nodes())
        else:
            NODEPANEL_STYLE["right"] = "-75%"
            show_element(OVERLAY_STYLE, False)
        last_selected_node_content[0] = ', '.join([el for el in get_selectable_nodes()])
        node_panel_children = [dbc.Row(last_selected_node_content[0], style=NODE_NAMES_STYLE), sum_chart,
                               timeseries_chart, sum_chart_links]
        timeseries_chart_nodes = get_selectable_nodes()
        timeseries_chart_links = get_selectable_links()
        show_element(SELECT_STYLE, not is_select)
        show_element(DESELECT_STYLE, is_select)
        last_plot[0] = timeseries_chart_nodes
        return node_panel_children, timeseries_chart_nodes, timeseries_chart_links

    last_selected_node_content: [] = [None]
    n_clicks_select_backup = [1]
    n_clicks_deselect_backup = [1]
    n_clicks_input_backup = [1]
    filter_n_clicks_backup = [1]
    dd_value_backup = [["0"]]
    checkbox_values_backup = [1]
    checklist_output_backup = [[]]
    slider_value_backup = [0]
    filter_icon_backup = [None]

    def input_button_clicked(values, current_elements):
        legal_values = []
        i = 0
        content = html.Div()
        while i < len(values):
            for elem in current_elements:
                # the infrastructure contains the value written to the input
                elem_id = elem["data"]["id"]
                if not is_edge(elem_id) and values[i].strip() in elem_id:
                    if elem_id not in legal_values and elem_id in get_selectable_nodes():
                        legal_values += [elem_id]
                        SUM_CHART_STYLE["display"] = "block"

                    if not is_node_panel_open():
                        open_node_panel()
                    content_string = "The following nodes were found: "
                    content = html.Div(content_string + " ".join(legal_values),
                                       style={"width": "50%", "position": "relative", "top": "0px", "left": "12px"})

            if not legal_values:
                close_node_panel()

                content = html.Div("Nothing found, please type a valid node id or node group!",
                                   style={"width": "50%", "position": "relative", "top": "0px", "left": "12px",
                                          "color": "red"})
            i += 1
        converted_legal_values = list(map(lambda x: {'id': x}, legal_values))
        all_selectable, selectable_legal_values = are_nodes_selectable(converted_legal_values)
        converted_selectable_legal_values = list(map(lambda x: x['id'], selectable_legal_values))
        set_selected_nodes(converted_selectable_legal_values)
        return converted_selectable_legal_values, content

    # check if element is an edge
    def is_edge(elem_id):
        if "$" in elem_id:
            return True
        else:
            return False

    def update_network_elements_from_filter(checkbox_value, current_elements=infrastructure["100"], slider_used=False):
        if not checklist_output_backup[0] or slider_used:
            checklist_output = infrastructure_to_cyto_dict(current_elements)
        else:
            checklist_output = checklist_output_backup[0]
        new_infrastructure_list = []
        if (checkbox_value != checkbox_values_backup[0] and checkbox_value) or slider_used:
            checkbox_values_backup[0] = checkbox_value
            for j in checkbox_value:
                for i in infrastructure_to_cyto_dict(current_elements):
                    # is the node classname the same as the checkbox value
                    class_if = i["classes"]
                    if is_edge(class_if):
                        source = class_if.split("$")[0]
                        target = class_if.split("$")[1]

                        source_in_filter = False
                        target_in_filter = False
                        if "fog" in source:
                            source_type = "fognode"
                        else:
                            source_type = set_type_of_node(source)
                        if "fog" in target:
                            target_type = "fognode"
                        else:
                            target_type = set_type_of_node(target)
                        for k in checkbox_value:
                            if source_type in set_type_of_node(k).lower():
                                source_in_filter = True
                            if target_type in set_type_of_node(k).lower():
                                target_in_filter = True
                        if source_in_filter and target_in_filter:
                            source_exists = False
                            target_exists = False
                            for elem in infrastructure_to_cyto_dict(current_elements):
                                if elem["data"]["id"] == source:
                                    source_exists = True
                                if elem["data"]["id"] == target:
                                    target_exists = True
                                if source_exists and target_exists:
                                    new_infrastructure_list.append(i)
                                    checklist_output_backup[0] = new_infrastructure_list
                                    break
                    else:
                        if "fog" in i["classes"]:
                            class_if = "fognode"
                        if class_if in set_type_of_node(j).lower():
                            new_infrastructure_list.append(i)
                            checklist_output_backup[0] = new_infrastructure_list
        elif checkbox_value != checkbox_values_backup[0] and not checkbox_value and not checkbox_value is None:
            checkbox_values_backup[0] = checkbox_value
            new_infrastructure_list = infrastructure_to_cyto_dict(current_elements)
            checklist_output_backup[0] = []
        elif checkbox_value:
            # if the slider has never been used and the filter has been used and a node was selected
            new_infrastructure_list = checklist_output
        else:
            new_infrastructure_list = infrastructure_to_cyto_dict(current_elements)
        return new_infrastructure_list

    def update_network_from_slider(slider_value, checkbox_value):
        # slider used
        if (slider_value != slider_value_backup[0]):
            slider_value_backup[0] = slider_value
            if not checkbox_value:
                return infrastructure_to_cyto_dict(infrastructure[str(slider_value)])
            else:
                return update_network_elements_from_filter(checkbox_value, infrastructure[str(slider_value)], True)
        else:
            new_elements = infrastructure[str(slider_value)]
            return update_network_elements_from_filter(checkbox_value, new_elements)

    @app.callback(
        Output(network, "tapNodeData"),
        Input("deselect", "n_clicks")
    )
    def trigger_update_click_again(n_clicks):
        if n_clicks == 0:
            return None
        return {"triggerHelper": True}

    @app.callback(
        Output(node_panel, 'style'),
        Output(node_panel, "children"),
        Output(timeseries_chart, component_property='figure'),
        Output(network, "stylesheet"),
        Output("select", "style"),
        Output("deselect", "style"),
        Output("overlay", "style"),
        Output(sum_chart, component_property="figure"),
        Output('container-button-basic', 'children'),
        Output('options_container', 'style'),
        Output('network', 'elements'),
        Output('network', 'layout'),
        Output('slider-value', 'children'),
        Output('filter', "className"),
        Output(sum_chart_links, component_property="figure"),

        Input(network, component_property='selectedNodeData'),
        Input("select", "n_clicks"),
        Input("deselect", "n_clicks"),
        Input(network, "tapNodeData"),
        Input(network, "selectedEdgeData"),
        Input('submit-val', 'n_clicks'),
        State('input', 'value'),
        [Input('dd_input', 'value')],
        Input('filter', 'n_clicks'),
        Input('dpdn', 'value'),
        Input('checkboxes', 'value'),
        Input('slider', 'value')

    )
    def update_click(selected_node_data, n_clicks_select, n_clicks_deselect, tap_node_data, selectedEgdeData, n_clicks,
                     value, dd_value, filter_n_clicks, layout_value, checkbox_value, slider_value):
        NODEPANEL_STYLE["width"] = "50%"
        CHART_STYLE["display"] = "block"
        SUM_CHART_LINKS_STYLE["display"] = "none"
        timeseries_chart_nodes = []
        timeseries_chart_links = []
        select_button_clicked = False
        deselect_button_clicked = False
        reset_dash_nodes()

        sum_chart_figure = sum_power_fig(node_measurements, timeseries_chart_nodes)
        sum_chart_links_figure = sum_power_fig(link_measurements, timeseries_chart_links)
        dd_helper = list(filter(lambda elem: not elem == "select all", dd_value))
        timeseries_chart_figure = power_fig(node_measurements, dd_helper)
        layout_output = None

        last_was_edge = False
        if last_plot[0]:
            if "$" in last_plot[0][0]:
                last_was_edge = True

        # Slider interaction
        new_elements = update_network_from_slider(slider_value, checkbox_value)

        if layout_value == 'preset':
            layout_output = None
        else:
            def helpermap(elem):
                if "position" in elem:
                    elem.pop("position")
                return elem

            new_elements = list(map(helpermap, new_elements))
            layout_output = {
                'name': layout_value,
                'animate': True
            }
        slider_text_value = 'Current selected timeslot: "{}"'.format(slider_value)
        # filter button interaction
        filter_output = None
        if filter_n_clicks == filter_n_clicks_backup[0]:
            if filter_n_clicks % 2 != 0:
                filter_icon = "open"
                filter_n_clicks_backup[0] += 1
                OPTIONS_CONTAINER["display"] = "flex"
            else:
                filter_icon = "close"
                filter_n_clicks_backup[0] += 1
                OPTIONS_CONTAINER["display"] = "none"
            filter_icon_backup[0] = filter_icon

        # dropdown interaction
        if dd_value != dd_value_backup[0] and dd_value:
            dd_elements = dd_value

            if "select all" in dd_value:
                set_selected_nodes(get_selectable_nodes())
                dd_elements = get_selectable_nodes()
            else:
                set_selected_nodes(dd_value)
            dd_value_backup[0] = dd_value
            node_panel_children = [dbc.Row(", ".join(dd_elements),
                                           style=NODE_NAMES_STYLE), sum_chart, timeseries_chart, sum_chart_links]
            SUM_CHART_STYLE["display"] = "block"
            timeseries_chart_figure = power_fig(node_measurements, dd_elements)
            sum_chart_figure = sum_power_fig(node_measurements, dd_elements)
            open_node_panel()

            last_plot[0] = dd_elements
            last_selected_node_content[0] = dd_elements
            return [NODEPANEL_STYLE, node_panel_children, timeseries_chart_figure, NETWORK_STYLESHEET, SELECT_STYLE,
                    DESELECT_STYLE, OVERLAY_STYLE, sum_chart_figure, "", OPTIONS_CONTAINER, new_elements, layout_output,
                    slider_text_value, filter_icon_backup[0], sum_chart_links_figure]
        else:

            measurments = node_measurements
            if last_was_edge:
                measurments = link_measurements
            sum_chart_figure = sum_power_fig(measurments, last_plot[0])
            timeseries_chart_figure = power_fig(measurments, last_plot[0], False if last_was_edge else True)
            node_panel_children = [dbc.Row(last_selected_node_content[0], style=NODE_NAMES_STYLE), sum_chart,
                                   timeseries_chart, filter_icon_backup[0], sum_chart_links]
            dd_value_backup[0] = dd_value

        # submit was clicked
        if n_clicks == n_clicks_input_backup[0]:
            n_clicks_input_backup[0] += 1
            # check if value is in network
            if not value:
                close_node_panel()
                content = html.Div("Nothing found, please type a valid node id or node group!",
                                   style={"width": "50%", "position": "relative", "top": "0px", "left": "12px",
                                          "color": "red"})
            else:
                legal_values, content = input_button_clicked(value.split(","), new_elements)
                if legal_values:
                    last_plot[0] = legal_values

            sum_chart_figure = sum_power_fig(measurments, last_plot[0])
            timeseries_chart_figure = power_fig(measurments, last_plot[0], False if last_was_edge else True)
            node_panel_children = [dbc.Row(', '.join(last_plot[0]),
                                           style=NODE_NAMES_STYLE), sum_chart, timeseries_chart, sum_chart_links]

            return [NODEPANEL_STYLE, node_panel_children, timeseries_chart_figure, NETWORK_STYLESHEET, SELECT_STYLE,
                    DESELECT_STYLE, OVERLAY_STYLE, sum_chart_figure, content, OPTIONS_CONTAINER, new_elements,
                    layout_output, slider_text_value, filter_icon_backup[0], sum_chart_links_figure]
        # select button was clicked
        if n_clicks_select == n_clicks_select_backup[0]:
            select_button_clicked = True
            node_panel_children, timeseries_chart_nodes, timeseries_chart_links = button_clicked(n_clicks_select_backup,
                                                                                                 True)
            timeseries_chart_figure = power_fig(node_measurements, timeseries_chart_nodes)
            CHART_STYLE["display"] = "none"
            SUM_CHART_STYLE["display"] = "block"
            SUM_CHART_LINKS_STYLE["display"] = "block"

            sum_chart_figure = sum_power_fig(node_measurements, timeseries_chart_nodes)
            sum_chart_links_figure = sum_power_fig(link_measurements, timeseries_chart_links)
            node_panel_children = [dbc.Row("All selectable nodes and edges", style=NODE_NAMES_STYLE),
                                   sum_chart,
                                   timeseries_chart, sum_chart_links]

        # deselect button was clicked
        if n_clicks_deselect == n_clicks_deselect_backup[0]:
            deselect_button_clicked = True
            node_panel_children, timeseries_chart_nodes, timeseries_chart_links = button_clicked(
                n_clicks_deselect_backup, False)
            timeseries_chart_figure = power_fig(node_measurements, timeseries_chart_nodes)
            sum_chart_links_figure = sum_power_fig(link_measurements, timeseries_chart_links)
            CHART_STYLE["display"] = "none"
            SUM_CHART_STYLE["display"] = "block"
            SUM_CHART_LINKS_STYLE["display"] = "block"
            node_panel_children = [dbc.Row("All selectable nodes and edges", style=NODE_NAMES_STYLE),
                                   sum_chart,
                                   timeseries_chart, sum_chart_links]

        if select_button_clicked or deselect_button_clicked:
            return [NODEPANEL_STYLE, node_panel_children, timeseries_chart_figure, NETWORK_STYLESHEET, SELECT_STYLE,
                    DESELECT_STYLE, OVERLAY_STYLE, sum_chart_figure, "", OPTIONS_CONTAINER, new_elements, layout_output,
                    slider_text_value, filter_icon_backup[0], sum_chart_links_figure]
        show_element(SELECT_STYLE, True)
        show_element(DESELECT_STYLE, False)
        show_element(OVERLAY_STYLE, False)
        # edge was clicked
        if not selected_node_data and not tap_node_data or selectedEgdeData \
                or (last_was_edge and not selected_node_data):
            if selectedEgdeData is None:
                close_node_panel()

            else:
                if not selectedEgdeData:
                    close_node_panel()

                    SUM_CHART_STYLE["display"] = "block"

                else:
                    open_node_panel()
                    timeseries_chart_edges = [el["id"] for el in selectedEgdeData]
                    last_selected_node_content[0] = [el["id"] for el in selectedEgdeData]
                    last_plot[0] = timeseries_chart_edges
                    SUM_CHART_STYLE["display"] = "block"

                node_panel_children = [dbc.Row(last_selected_node_content[0], style=NODE_NAMES_STYLE), sum_chart,
                                       timeseries_chart, sum_chart_links]
                timeseries_chart_figure = power_fig(link_measurements, last_plot[0], False)
                sum_chart_figure = sum_power_fig(link_measurements, last_plot[0])

            return [NODEPANEL_STYLE, node_panel_children, timeseries_chart_figure, NETWORK_STYLESHEET, SELECT_STYLE,
                    DESELECT_STYLE, OVERLAY_STYLE, sum_chart_figure, "", OPTIONS_CONTAINER, new_elements, layout_output,
                    slider_text_value, filter_icon_backup[0], sum_chart_links_figure]

        sum_chart_figure = sum_power_fig(node_measurements, timeseries_chart_nodes)

        if selected_node_data is None:
            if not select_button_clicked:
                close_node_panel()
        else:
            # list is empty
            all_selectable, legal_nodes_list = are_nodes_selectable(selected_node_data)
            if not selected_node_data:
                close_node_panel()
                timeseries_chart_nodes = last_plot[0]

                node_panel_children = [dbc.Row(last_selected_node_content[0], style=NODE_NAMES_STYLE), sum_chart,
                                       timeseries_chart, sum_chart_links]
            else:
                # selected list is not empty and node is selectable
                # if are_nodes_selectable returns selected_node_data
                if (all_selectable or legal_nodes_list) and tap_node_data["id"] in get_selectable_nodes():
                    last_selected_node_content[0] = ', '.join([el["id"] for el in legal_nodes_list])
                    set_selected_nodes([el["id"] for el in legal_nodes_list])
                    timeseries_chart_nodes = [el["id"] for el in legal_nodes_list]
                    last_plot[0] = timeseries_chart_nodes
                    open_node_panel()

                    sum_chart_figure = sum_power_fig(node_measurements, timeseries_chart_nodes)
                    node_panel_children = [dbc.Row(last_selected_node_content[0], style=NODE_NAMES_STYLE),
                                           sum_chart,
                                           timeseries_chart, sum_chart_links]

                # clicked node ist not selectable
                # if are_nodes_selectable returns empty list
                else:
                    last_selected_nodes_id_list = last_plot[0]
                    if last_selected_nodes_id_list is not None and is_node_panel_open():
                        set_selected_nodes(last_selected_nodes_id_list)
                        node_panel_children = [dbc.Row(last_selected_node_content[0], style=NODE_NAMES_STYLE),
                                               dbc.Row(sum_chart, style=SUM_PLOT_CONTAINER), timeseries_chart,
                                               sum_chart_links]
                        timeseries_chart_nodes = last_plot[0]
                        open_node_panel()
        timeseries_chart_figure = power_fig(node_measurements, timeseries_chart_nodes)
        sum_chart_figure = sum_power_fig(node_measurements, timeseries_chart_nodes)
        SUM_CHART_STYLE["display"] = "block"
        sum_chart_figure = sum_power_fig(node_measurements, timeseries_chart_nodes)

        return [NODEPANEL_STYLE, node_panel_children, timeseries_chart_figure, NETWORK_STYLESHEET, SELECT_STYLE,
                DESELECT_STYLE, OVERLAY_STYLE, sum_chart_figure, "", OPTIONS_CONTAINER, new_elements, layout_output,
                slider_text_value, filter_icon_backup[0], sum_chart_links_figure]

    app.run_server(debug=True)


if __name__ == "__main__":
    main()
