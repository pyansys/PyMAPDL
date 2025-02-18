# Script to calculate the first natural frequecy of a rotor for a given set of properties
import click

# Import packages
import numpy as np

from ansys.mapdl.core import launch_mapdl


@click.command()
@click.argument(
    "n_blades",
)  # arguments are mandatory
@click.option("--blade_length", default=0.2, help="Length of each blade.")  # optionals
@click.option(
    "--elastic_modulus", default=200e9, help="Elastic modulus of the material."
)
@click.option("--density", default=7850, help="Density of the material.")
def main(n_blades, blade_length, elastic_modulus, density):
    print(
        "Initialize script with values:\n"
        f"Number of blades: {n_blades}\nBlade length: {blade_length} m\n"
        f"Elastic modulus: {elastic_modulus/1E9} GPa\nDensity: {density} Kg/m3"
    )
    # Launch MAPDL
    mapdl = launch_mapdl(port=50052)
    mapdl.clear()
    mapdl.prep7()

    # Convert input properties
    n_blades = float(n_blades)

    # Define other properties
    center_radious = 0.1
    blade_thickness = 0.02
    section_length = 0.06

    ## Define material
    # Material 1: Steel
    mapdl.mp("NUXY", 1, 0.31)
    mapdl.mp("DENS", 1, density)
    mapdl.mp("EX", 1, elastic_modulus)

    ## Geometry
    # Plot center
    area_cyl = mapdl.cyl4(0, 0, center_radious)

    # Define path for dragging
    k0 = mapdl.k(x=0, y=0, z=0)
    k1 = mapdl.k(x=0, y=0, z=section_length)

    line_path = mapdl.l(k0, k1)

    mapdl.vdrag(area_cyl, nlp1=line_path)
    center_vol = mapdl.geometry.vnum[0]

    # Create spline
    precision = 5
    advance = section_length / precision

    spline = []
    for i in range(precision + 1):
        if i != 0:
            k0 = mapdl.k("", x_, y_, z_)
        angle_ = i * (360 / n_blades) / precision
        x_ = section_length * np.cos(np.deg2rad(angle_))
        y_ = section_length * np.sin(np.deg2rad(angle_))
        z_ = i * advance

        if i != 0:
            k1 = mapdl.k("", x_, y_, z_)
            spline.append(mapdl.l(k0, k1))

    # Merge lines
    mapdl.nummrg("kp")

    # Create area of the blade
    point_0 = mapdl.k("", center_radious * 0.6, -blade_thickness / 2, 0)
    point_1 = mapdl.k("", center_radious + blade_length, -blade_thickness / 2, 0)
    point_2 = mapdl.k("", center_radious + blade_length, blade_thickness / 2, 0)
    point_3 = mapdl.k("", center_radious, blade_thickness / 2, 0)
    blade_area = mapdl.a(point_0, point_1, point_2, point_3)

    # Drag area to
    mapdl.vdrag(
        blade_area,
        nlp1=spline[0],
        nlp2=spline[1],
        nlp3=spline[2],
        nlp4=spline[3],
        nlp5=spline[4],
    )

    # Glue blades
    mapdl.allsel()
    mapdl.vsel("u", vmin=center_vol)
    mapdl.vadd("all")
    blade_volu = mapdl.geometry.vnum[0]

    # Define cutting blade and circle
    mapdl.allsel()
    mapdl.vsbv(blade_volu, center_vol, keep2="keep")
    blade_volu = mapdl.geometry.vnum[-1]

    # Define symmetry
    mapdl.csys(1)  # switch to cylindrical
    mapdl.vgen(n_blades, blade_volu, dy=360 / n_blades, imove=0)
    mapdl.csys(0)  # switch to global coordinate system

    mapdl.vplot(savefig="volumes.jpg")

    # Glue/add volumes
    mapdl.allsel()
    mapdl.vadd("all")
    center_vol = mapdl.geometry.vnum[-1]

    # Mesh
    mapdl.allsel()
    mapdl.et(1, "SOLID186")
    mapdl.esize(blade_thickness / 2)
    mapdl.mshape(1, "3D")
    mapdl.vmesh("all")

    # Apply loads
    mapdl.nsel("all")
    mapdl.nsel("r", "loc", "z", 0)
    mapdl.csys(1)
    mapdl.nsel("r", "loc", "x", 0, center_radious)
    mapdl.d("all", "ux", 0)
    mapdl.d("all", "uy", 0)
    mapdl.d("all", "uz", 0)
    mapdl.csys(0)

    # Solve
    mapdl.allsel()
    mapdl.slashsolu()
    nmodes = 10  # Get the first 10 modes
    print("Solving...")
    output = mapdl.modal_analysis(nmode=nmodes)

    mapdl.post1()
    modes = mapdl.set("list").to_array()
    freqs = modes[:, 1]

    # Output values
    first_frequency = freqs[0]
    print(f"The first natural frequency is {first_frequency} Hz.")


if __name__ == "__main__":
    main()
