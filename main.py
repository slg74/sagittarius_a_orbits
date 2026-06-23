"""
3-D Keplerian simulation of the S-star cluster orbiting Sagittarius A*.

Orbital elements from Gillessen et al. 2017 (ApJ 837, 30) with S2 periapsis
updated to GRAVITY Collaboration 2018.  Schwarzschild (GR) precession is applied
to S2 — the GRAVITY Collaboration measured ~0.2°/orbit in 2020.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D          # noqa: F401 — registers 3D projection
from matplotlib.animation import FuncAnimation, PillowWriter

# ── Physical constants (CODATA 2018 / IAU 2012) ───────────────────────────────
G_SI     = 6.67430e-11          # m³ kg⁻¹ s⁻²  (CODATA 2018)
C_SI     = 299_792_458.0        # m/s            (exact)
M_SUN    = 1.98892e30           # kg             (IAU 2015)
AU_TO_M  = 149_597_870_700.0    # m/AU           (IAU 2012, exact)
PC_TO_AU = 206_264.806_247      # AU/pc

R0_PC    = 8178.0               # GC distance, parsecs (GRAVITY Collaboration 2019)
R0_AU    = R0_PC * PC_TO_AU     # ≈ 1.687e9 AU
AS_TO_AU = R0_AU * np.pi / (180 * 3600)   # arcsec → AU  ≈ 8178 AU/"
M_BH     = 4.154e6 * M_SUN     # Sgr A* mass in kg (GRAVITY 2019)

# ── S-star orbital elements ────────────────────────────────────────────────────
# Source: Gillessen et al. 2017 Table 4; t_peri(S2) from GRAVITY 2018.
# Columns: name, a (arcsec), e, i (°), Ω (°), ω (°), t_peri (yr), P (yr), color
STARS = [
    ('S2',  0.1255, 0.8843, 134.18, 226.94,  65.51, 2018.38, 16.05, '#ff4444'),
    ('S8',  0.4047, 0.8031,  74.37, 315.43, 346.70, 1983.64, 66.70, '#ffaa00'),
    ('S12', 0.2987, 0.8883,  33.56, 230.84, 317.90, 1995.53, 53.30, '#44bbff'),
    ('S13', 0.2692, 0.4250,  24.70,  74.42, 245.70, 2006.10, 45.50, '#44ff88'),
    ('S14', 0.2874, 0.9761, 100.59, 226.36, 340.00, 2000.12, 55.30, '#dd66ff'),
]


def schwarzschild_precession_rate(a_arcsec, e, period_yr):
    """Return Schwarzschild precession rate in degrees/year for an orbit around Sgr A*."""
    a_m = a_arcsec * AS_TO_AU * AU_TO_M
    delta_omega_rad = 6 * np.pi * G_SI * M_BH / (a_m * (1 - e**2) * C_SI**2)
    return np.degrees(delta_omega_rad) / period_yr


def solve_kepler(M, e):
    """Newton-Raphson solver for Kepler's equation  E - e·sin(E) = M."""
    E = M.copy()
    for _ in range(100):
        dE = (M - E + e * np.sin(E)) / (1 - e * np.cos(E))
        E += dE
        if np.all(np.abs(dE) < 1e-12):
            break
    return E


def orbit_xyz(t_yr, a_as, e, i_deg, Omega_deg, omega0_deg, t_peri, period_yr,
              pn_rate=0.0):
    """
    Compute 3-D position in AU at times t_yr (scalar or array).

    pn_rate: Schwarzschild precession rate in degrees/year applied to ω.
    Uses the Thiele-Innes rotation: Rz(Ω) · Rx(i) · Rz(ω).
    """
    t     = np.atleast_1d(np.asarray(t_yr, dtype=float))
    a_au  = a_as * AS_TO_AU
    omega = np.deg2rad(omega0_deg + pn_rate * (t - t_peri))      # time-varying ω
    M     = (2 * np.pi * ((t - t_peri) / period_yr)) % (2 * np.pi)
    E     = solve_kepler(M, e)
    nu    = 2 * np.arctan2(np.sqrt(1 + e) * np.sin(E / 2),
                            np.sqrt(1 - e) * np.cos(E / 2))
    r     = a_au * (1 - e**2) / (1 + e * np.cos(nu))

    x_o, y_o = r * np.cos(nu), r * np.sin(nu)

    O  = np.deg2rad(Omega_deg)
    ii = np.deg2rad(i_deg)
    cO, sO = np.cos(O),     np.sin(O)
    ci, si = np.cos(ii),    np.sin(ii)
    cw, sw = np.cos(omega), np.sin(omega)

    x = (cO*cw - sO*sw*ci)*x_o + (-cO*sw - sO*cw*ci)*y_o
    y = (sO*cw + cO*sw*ci)*x_o + (-sO*sw + cO*cw*ci)*y_o
    z = (sw*si)*x_o             + (cw*si)*y_o
    return x, y, z


def full_ellipse(a_as, e, i_deg, Omega_deg, omega_deg, t_peri, period_yr):
    """Return one full orbital ellipse in 3-D (static reference, no precession)."""
    t = np.linspace(t_peri, t_peri + period_yr, 1000)
    return orbit_xyz(t, a_as, e, i_deg, Omega_deg, omega_deg, t_peri, period_yr)


def main():
    T_START      = 2000.0
    T_END        = 2050.0
    N_FRAMES     = 800
    TRAIL_FRAMES = 90     # animation frames shown as trail

    t_anim = np.linspace(T_START, T_END, N_FRAMES)

    # ── Pre-compute positions ──────────────────────────────────────────────────
    pn_rates = {}
    all_xyz  = {}
    for name, a, e, i, O, w, tp, P, _ in STARS:
        rate = schwarzschild_precession_rate(a, e, P) if name == 'S2' else 0.0
        pn_rates[name] = rate
        all_xyz[name]  = orbit_xyz(t_anim, a, e, i, O, w, tp, P, rate)

    s2_pn_per_orbit = pn_rates['S2'] * 16.05
    print(f"S2 Schwarzschild precession: {pn_rates['S2']:.5f}°/yr  "
          f"= {s2_pn_per_orbit:.3f}°/orbit  (measured: ~0.20°/orbit)")

    # ── Figure setup ──────────────────────────────────────────────────────────
    fig = plt.figure(figsize=(9, 7), facecolor='black')
    ax  = fig.add_subplot(111, projection='3d', facecolor='black')

    LIM = 5500
    ax.set_xlim(-LIM, LIM)
    ax.set_ylim(-LIM, LIM)
    ax.set_zlim(-LIM, LIM)
    ax.set_xlabel('X (AU)', color='#777777', labelpad=6)
    ax.set_ylabel('Y (AU)', color='#777777', labelpad=6)
    ax.set_zlabel('Z (AU)', color='#777777', labelpad=6)
    ax.tick_params(colors='#555555', labelsize=6)
    ax.set_title('S-Star Cluster — Sagittarius A*\n'
                 'Real Keplerian orbits · Schwarzschild precession (S2)',
                 color='white', fontsize=11, pad=10, linespacing=1.5)

    for pane in (ax.xaxis.pane, ax.yaxis.pane, ax.zaxis.pane):
        pane.fill = False
        pane.set_edgecolor('#0d0d0d')
    ax.grid(True, color='#0d0d0d', linewidth=0.4)

    # Sgr A* — bright dot with gold halo
    ax.scatter([0], [0], [0], s=160, c='white', zorder=10,
               edgecolors='gold', linewidths=1.0, label='Sgr A*')

    # Static reference ellipses (no precession — one fixed epoch)
    for name, a, e, i, O, w, tp, P, color in STARS:
        xe, ye, ze = full_ellipse(a, e, i, O, w, tp, P)
        ax.plot(xe, ye, ze, color=color, alpha=0.10, linewidth=0.7, zorder=1)

    # Animated artists
    trail_lines = {}
    dot_markers = {}
    for name, *_, color in STARS:
        line, = ax.plot([], [], [], '-', color=color, alpha=0.55,
                        linewidth=1.1, zorder=3)
        dot,  = ax.plot([], [], [], 'o', color=color, markersize=5,
                        markeredgecolor='white', markeredgewidth=0.3,
                        zorder=5, label=name)
        trail_lines[name] = line
        dot_markers[name] = dot

    ax.legend(loc='upper right', fontsize=7.5, facecolor='#0a0a0a',
              edgecolor='#444444', labelcolor='white', markerscale=1.1,
              framealpha=0.9)

    year_label = ax.text2D(0.03, 0.95, '', transform=ax.transAxes,
                            color='white', fontsize=10, va='top',
                            fontfamily='monospace')
    ax.text2D(0.03, 0.04,
              f'S2 GR precession:  {s2_pn_per_orbit:.3f}° / orbit',
              transform=ax.transAxes, color='#888888', fontsize=7)
    ax.text2D(0.03, 0.01,
              'Orbital elements: Gillessen et al. 2017 · GRAVITY Collaboration 2018',
              transform=ax.transAxes, color='#555555', fontsize=6)

    def make_update(rotate):
        def update(fi):
            if rotate:
                ax.view_init(elev=28, azim=(fi / N_FRAMES) * 720)
            year_label.set_text(f'Year  {t_anim[fi]:.1f}')
            t0 = max(0, fi - TRAIL_FRAMES)
            for name, *_ in STARS:
                x, y, z = all_xyz[name]
                trail_lines[name].set_data_3d(x[t0:fi+1], y[t0:fi+1], z[t0:fi+1])
                dot_markers[name].set_data_3d([x[fi]], [y[fi]], [z[fi]])
            return list(trail_lines.values()) + list(dot_markers.values()) + [year_label]
        return update

    print(f"Animating {N_FRAMES} frames ({T_START:.0f}–{T_END:.0f})...")

    for out, rotate in [('sgr_A.gif', True), ('sgr_A_static.gif', False)]:
        if not rotate:
            ax.view_init(elev=28, azim=45)
        anim = FuncAnimation(fig, make_update(rotate),
                             frames=N_FRAMES, interval=40, blit=False)
        print(f"Saving {out}...")
        anim.save(out, writer=PillowWriter(fps=25), dpi=80)
        print(f"  Done — {out}")

    plt.close()
    print("All done.")


if __name__ == '__main__':
    main()
