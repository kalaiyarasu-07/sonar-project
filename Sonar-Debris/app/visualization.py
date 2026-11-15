
import numpy as np
import plotly.graph_objects as go

BACKGROUND = "#0D1420"
GRID = "#263449"
CYAN = "#22D3EE"


def create_scan_figure(points, cycle_number=0):
    fig = go.Figure()

    # Radar distance rings
    theta = np.linspace(0, np.pi, 181)

    for radius in [2, 5, 10]:
        fig.add_trace(go.Scatter(
            x=radius * np.cos(theta),
            y=radius * np.sin(theta),
            mode="lines",
            line=dict(color="#334155", width=1, dash="dot"),
            hoverinfo="skip",
            showlegend=False
        ))

    # Scanner position
    fig.add_trace(go.Scatter(
        x=[0], y=[0],
        mode="markers",
        marker=dict(size=12, color="#F59E0B", symbol="diamond"),
        name="Scanner"
    ))

    # Draw detected object contours
    if points:
        clusters = {}

        for p in points:
            cluster_id = p.get("cluster", 0)
            clusters.setdefault(cluster_id, []).append(p)

        for cluster_id, group in clusters.items():
            group = sorted(group, key=lambda p: p["angle"])

            x = [p["x"] for p in group]
            y = [p["y"] for p in group]

            # Connect measured surface points
            fig.add_trace(go.Scatter(
                x=x,
                y=y,
                mode="lines+markers",
                line=dict(color=CYAN, width=4),
                marker=dict(size=7, color=CYAN),
                name=f"Object {cluster_id + 1}"
            ))

    else:
        fig.add_annotation(
            x=0, y=5,
            text="NO OBJECTS DETECTED",
            showarrow=False,
            font=dict(size=18, color="#94A3B8")
        )

    fig.update_layout(
        title=f"SONAR DEBRIS | RECONSTRUCTION | CYCLE {cycle_number}",
        paper_bgcolor=BACKGROUND,
        plot_bgcolor=BACKGROUND,
        font=dict(color="#E2E8F0"),
        xaxis=dict(
            title="X Coordinate (cm)",
            range=[-11, 11],
            gridcolor=GRID,
            zerolinecolor="#64748B"
        ),
        yaxis=dict(
            title="Y Coordinate (cm)",
            range=[-1, 11],
            gridcolor=GRID,
            zerolinecolor="#64748B",
            scaleanchor="x",
            scaleratio=1
        ),
        showlegend=True,
        height=650,
        margin=dict(l=40, r=30, t=70, b=40)
    )

    return fig


def create_distance_profile(scan_data, cycle_number=0):
    angles = []
    distances = []

    for p in scan_data:
        angles.append(p["angle"])
        distances.append(
            p["distance"] if p["distance"] > 0 else None
        )

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=angles,
        y=distances,
        mode="lines+markers",
        line=dict(color=CYAN, width=2),
        marker=dict(size=4),
        name="Distance"
    ))

    fig.add_hline(
        y=10,
        line_dash="dash",
        line_color="#F59E0B",
        annotation_text="10 cm detection limit"
    )

    fig.update_layout(
        title=f"DISTANCE PROFILE | CYCLE {cycle_number}",
        paper_bgcolor=BACKGROUND,
        plot_bgcolor=BACKGROUND,
        font=dict(color="#E2E8F0"),
        xaxis=dict(title="Servo Angle (degrees)", gridcolor=GRID),
        yaxis=dict(title="Distance (cm)", gridcolor=GRID),
        height=350
    )

    return fig
