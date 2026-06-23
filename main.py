import math
import random
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

AU       = 149597870700   # meters per AU
G        = 6.67408e-11    # gravitational constant
TIMESTEP = 3600 * 6       # 6 hours per simulation step

solar_mass  = 1.989e30
sgr_a_mass  = 4e6 * 5 * solar_mass  # 4M solar masses, ×5 to speed up orbits

# (x_m, y_m, vx_m/s, vy_m/s, mass_kg, color, label)
STARS = [
    (0,           0,  0,            0,           sgr_a_mass,       'lime',   'Sgr A*'),
    (-100 * AU,  10,  0,       7005.3e3,  12.5 * solar_mass,  'red',    'S2'),
    ( 120 * AU,  10,  0,      -8000.0e3,  15.0 * solar_mass,  'yellow', 'S8'),
    (-130 * AU,  10,  0,       6000.0e3,  15.0 * solar_mass,  'orange', 'S12'),
    ( 250 * AU,  10,  0,      -5000.13e3, 15.0 * solar_mass,  'lime',   'S13'),
    (-220 * AU,  10,  0,       5500.13e3, 15.0 * solar_mass,  'teal',   'S14'),
]


def simulate(n_steps):
    xs  = [s[0] for s in STARS]
    ys  = [s[1] for s in STARS]
    vxs = [s[2] for s in STARS]
    vys = [s[3] for s in STARS]
    ms  = [s[4] for s in STARS]
    n   = len(STARS)

    hist_x = [[] for _ in range(n)]
    hist_y = [[] for _ in range(n)]

    for step in range(n_steps):
        if step % 500 == 0:
            print(f"  step {step}/{n_steps}")

        for i in range(n):
            hist_x[i].append(xs[i])
            hist_y[i].append(ys[i])

        ax_ = [0.0] * n
        ay_ = [0.0] * n
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                dx = xs[j] - xs[i]
                dy = ys[j] - ys[i]
                r  = math.sqrt(dx * dx + dy * dy)
                f  = G * ms[i] * ms[j] / (r * r)
                th = math.atan2(dy, dx)
                ax_[i] += f * math.cos(th) / ms[i]
                ay_[i] += f * math.sin(th) / ms[i]

        for i in range(n):
            vxs[i] += ax_[i] * TIMESTEP
            vys[i] += ay_[i] * TIMESTEP
            xs[i]  += vxs[i] * TIMESTEP
            ys[i]  += vys[i] * TIMESTEP

    return hist_x, hist_y


def main():
    N_SIM      = 3000  # ~2 simulation years; S2 completes ~9 orbits
    FRAME_STEP = 6     # render every 6th step → 500 gif frames at 30 fps ≈ 17s
    TRAIL      = 300   # sim-steps of fading trail per star

    print("Simulating orbits...")
    hist_x, hist_y = simulate(N_SIM)
    frame_steps = list(range(0, N_SIM, FRAME_STEP))
    print(f"  {len(frame_steps)} frames to animate.")

    # ── figure ────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(9, 7), facecolor='black')
    ax.set_facecolor('black')
    XLIM, YLIM = 330, 270
    ax.set_xlim(-XLIM, XLIM)
    ax.set_ylim(-YLIM, YLIM)
    ax.set_aspect('equal')
    ax.set_xlabel('AU', color='#aaaaaa', fontsize=10)
    ax.set_ylabel('AU', color='#aaaaaa', fontsize=10)
    ax.set_title('Stars Orbiting Sagittarius A*', color='white', fontsize=13, pad=10)
    ax.tick_params(colors='#aaaaaa', labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor('#333333')
    ax.grid(True, color='#111111', linewidth=0.5, zorder=0)

    # static background stars
    rng = random.Random(7)
    bx = [rng.uniform(-XLIM, XLIM) for _ in range(60)]
    by = [rng.uniform(-YLIM, YLIM) for _ in range(60)]
    ax.scatter(bx, by, s=0.6, c='white', zorder=1, alpha=0.7)

    colors    = [s[5] for s in STARS]
    labels    = [s[6] for s in STARS]
    dot_sizes = [150 if i == 0 else 30 for i in range(len(STARS))]

    trail_lines = []
    dot_markers = []
    for i, (color, label) in enumerate(zip(colors, labels)):
        line, = ax.plot([], [], '-', color=color, alpha=0.35, linewidth=0.9, zorder=2)
        dot = ax.scatter([], [], s=dot_sizes[i], c=color, zorder=4,
                         label=label,
                         edgecolors='white' if i == 0 else 'none',
                         linewidths=0.5)
        trail_lines.append(line)
        dot_markers.append(dot)

    ax.legend(loc='upper right', fontsize=8,
              facecolor='#111111', edgecolor='#555555', labelcolor='white',
              markerscale=0.9, framealpha=0.85)

    def update(fi):
        step    = frame_steps[fi]
        t_start = max(0, step - TRAIL)
        for i in range(len(STARS)):
            px = [v / AU for v in hist_x[i][t_start:step + 1]]
            py = [v / AU for v in hist_y[i][t_start:step + 1]]
            trail_lines[i].set_data(px, py)
            if px:
                dot_markers[i].set_offsets([[px[-1], py[-1]]])
        return trail_lines + dot_markers

    print("Building animation...")
    anim = FuncAnimation(fig, update, frames=len(frame_steps), interval=33, blit=True)

    out = 'sgr_A.gif'
    print(f"Saving {out} (this takes a minute or two)...")
    anim.save(out, writer=PillowWriter(fps=30), dpi=90)
    plt.close()
    print(f"Done — saved to {out}")


if __name__ == '__main__':
    main()
