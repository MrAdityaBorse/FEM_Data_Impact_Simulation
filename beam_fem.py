from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np


@dataclass(frozen=True)
class Node2D:
    """A 2D node with 3 DOFs: (ux, uy, rz)."""

    id: int
    x: float
    y: float


@dataclass
class MaterialSection:
    """Linear elastic material and section properties for a 2D frame element."""

    youngs_modulus: float  # E
    area: float  # A
    second_moment: float  # I (about z for out-of-plane bending)


@dataclass
class DistributedLoadLocal:
    """Uniform distributed load in local element axes (per unit length).

    qx acts along local +x (axial), qy along local +y (transverse).
    Positive directions follow the local element axes.
    """

    qx: float = 0.0
    qy: float = 0.0


class BeamElement2D:
    """Euler-Bernoulli 2D frame element (6 DOFs: 3 per node).

    Local DOF ordering: [u1, v1, rz1, u2, v2, rz2].
    """

    def __init__(
        self,
        id: int,
        node_i: Node2D,
        node_j: Node2D,
        material: MaterialSection,
        udl_local: Optional[DistributedLoadLocal] = None,
    ) -> None:
        self.id = id
        self.node_i = node_i
        self.node_j = node_j
        self.material = material
        self.udl_local = udl_local

        dx = self.node_j.x - self.node_i.x
        dy = self.node_j.y - self.node_i.y
        self.length = float(math.hypot(dx, dy))
        if self.length <= 0.0:
            raise ValueError(f"Element {id} has zero length.")
        self.cos = dx / self.length
        self.sin = dy / self.length

    def local_stiffness(self) -> np.ndarray:
        """6x6 local stiffness matrix in element coordinates."""
        E = self.material.youngs_modulus
        A = self.material.area
        I = self.material.second_moment
        L = self.length

        # Axial and bending contributions for an Euler-Bernoulli frame element
        k = np.zeros((6, 6), dtype=float)

        # Axial
        EA_L = E * A / L
        k[0, 0] = EA_L
        k[0, 3] = -EA_L
        k[3, 0] = -EA_L
        k[3, 3] = EA_L

        # Bending (about z) - standard 2D frame element
        EI = E * I
        L2 = L * L
        L3 = L2 * L
        c1 = 12.0 * EI / L3
        c2 = 6.0 * EI / L2
        c3 = 4.0 * EI / L
        c4 = 2.0 * EI / L

        # rows/cols: [u1, v1, rz1, u2, v2, rz2]
        k[1, 1] = c1
        k[1, 2] = c2
        k[1, 4] = -c1
        k[1, 5] = c2

        k[2, 1] = c2
        k[2, 2] = c3
        k[2, 4] = -c2
        k[2, 5] = c4

        k[4, 1] = -c1
        k[4, 2] = -c2
        k[4, 4] = c1
        k[4, 5] = -c2

        k[5, 1] = c2
        k[5, 2] = c4
        k[5, 4] = -c2
        k[5, 5] = c3

        return k

    def transformation(self) -> np.ndarray:
        """6x6 transformation matrix from local to global DOFs.

        T such that: d_global = T @ d_local, F_global = T @ F_local
        and K_global = T @ K_local @ T.T (if using forces in global).
        Here we use K_g = T.T @ K_l @ T and F_g = T.T @ F_l consistently
        for assembly with d_g. Both conventions are equivalent when used consistently.
        """
        c = self.cos
        s = self.sin
        # Rotation for a node's [u, v, rz]
        R = np.array([[c, s, 0.0], [-s, c, 0.0], [0.0, 0.0, 1.0]], dtype=float)
        T = np.zeros((6, 6), dtype=float)
        T[0:3, 0:3] = R
        T[3:6, 3:6] = R
        return T

    def global_stiffness(self) -> np.ndarray:
        k_local = self.local_stiffness()
        T = self.transformation()
        # Using standard convention: K_global = T.T @ K_local @ T
        return T.T @ k_local @ T

    def equivalent_nodal_load_local(self) -> np.ndarray:
        """Equivalent nodal forces in local coordinates for uniform distributed load.

        For qy (transverse, +local y):
          [0, qy*L/2, qy*L^2/12, 0, qy*L/2, -qy*L^2/12]

        For qx (axial, +local x):
          [qx*L/2, 0, 0, qx*L/2, 0, 0]
        """
        L = self.length
        f = np.zeros(6, dtype=float)
        if self.udl_local is None:
            return f
        if self.udl_local.qx:
            qx = float(self.udl_local.qx)
            f += np.array([qx * L / 2.0, 0.0, 0.0, qx * L / 2.0, 0.0, 0.0])
        if self.udl_local.qy:
            qy = float(self.udl_local.qy)
            f += np.array([0.0, qy * L / 2.0, qy * L * L / 12.0, 0.0, qy * L / 2.0, -qy * L * L / 12.0])
        return f

    def equivalent_nodal_load_global(self) -> np.ndarray:
        f_local = self.equivalent_nodal_load_local()
        T = self.transformation()
        # F_global = T.T @ F_local (consistent with K_global = T.T @ K_local @ T)
        return T.T @ f_local


class Beam2DModel:
    """Finite element model for 2D Euler-Bernoulli frames/beams."""

    def __init__(self) -> None:
        self.nodes: Dict[int, Node2D] = {}
        self.elements: List[BeamElement2D] = []
        self._next_node_id = 1
        self._next_element_id = 1
        # Boundary conditions: dof_index -> prescribed displacement value
        self.prescribed: Dict[int, float] = {}
        # Nodal concentrated loads (global DOFs): dof_index -> force value
        self.nodal_forces: Dict[int, float] = {}

    # --- Model building ---

    def add_node(self, x: float, y: float) -> int:
        node_id = self._next_node_id
        self.nodes[node_id] = Node2D(node_id, float(x), float(y))
        self._next_node_id += 1
        return node_id

    def add_element(
        self,
        node_i_id: int,
        node_j_id: int,
        material: MaterialSection,
        udl_local: Optional[DistributedLoadLocal] = None,
    ) -> int:
        node_i = self.nodes[node_i_id]
        node_j = self.nodes[node_j_id]
        elem_id = self._next_element_id
        self.elements.append(BeamElement2D(elem_id, node_i, node_j, material, udl_local))
        self._next_element_id += 1
        return elem_id

    # --- DOF helpers ---

    def num_dofs(self) -> int:
        return 3 * len(self.nodes)

    def dof_indices_for_node(self, node_id: int) -> Tuple[int, int, int]:
        # Global DOF ordering: [ux1, uy1, rz1, ux2, uy2, rz2, ...]
        if node_id not in self.nodes:
            raise KeyError(f"Unknown node id: {node_id}")
        base = (node_id - 1) * 3
        return base + 0, base + 1, base + 2

    def fix_node(self, node_id: int, ux: bool = True, uy: bool = True, rz: bool = True, values: Optional[Tuple[float, float, float]] = None) -> None:
        """Prescribe DOFs at a node. Defaults to zero displacements/rotation."""
        dof_ids = self.dof_indices_for_node(node_id)
        vals = values if values is not None else (0.0, 0.0, 0.0)
        for enabled, dof, val in zip((ux, uy, rz), dof_ids, vals):
            if enabled:
                self.prescribed[dof] = float(val)

    def prescribe_dof(self, dof_index: int, value: float = 0.0) -> None:
        self.prescribed[dof_index] = float(value)

    def add_nodal_force(self, node_id: int, fx: float = 0.0, fy: float = 0.0, mz: float = 0.0) -> None:
        dof_ux, dof_uy, dof_rz = self.dof_indices_for_node(node_id)
        if fx:
            self.nodal_forces[dof_ux] = self.nodal_forces.get(dof_ux, 0.0) + float(fx)
        if fy:
            self.nodal_forces[dof_uy] = self.nodal_forces.get(dof_uy, 0.0) + float(fy)
        if mz:
            self.nodal_forces[dof_rz] = self.nodal_forces.get(dof_rz, 0.0) + float(mz)

    # --- Assembly ---

    def assemble_global_stiffness_and_load(self) -> Tuple[np.ndarray, np.ndarray]:
        n_dof = self.num_dofs()
        K = np.zeros((n_dof, n_dof), dtype=float)
        F = np.zeros(n_dof, dtype=float)

        # Element contributions
        for elem in self.elements:
            kg = elem.global_stiffness()
            dofs_i = self.dof_indices_for_node(elem.node_i.id)
            dofs_j = self.dof_indices_for_node(elem.node_j.id)
            edofs = (*dofs_i, *dofs_j)
            # Stiffness assembly
            for a in range(6):
                A_idx = edofs[a]
                for b in range(6):
                    B_idx = edofs[b]
                    K[A_idx, B_idx] += kg[a, b]
            # Equivalent nodal loads from distributed loads
            fe = elem.equivalent_nodal_load_global()
            for a in range(6):
                A_idx = edofs[a]
                F[A_idx] += fe[a]

        # Nodal concentrated loads
        for dof_idx, force_value in self.nodal_forces.items():
            F[dof_idx] += float(force_value)

        return K, F

    # --- Solve ---

    def solve(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Solve for displacements and reactions.

        Returns (d, F_total, reactions) where:
          - d: global displacement vector (size n_dof)
          - F_total: total global force vector including distributed and nodal loads
          - reactions: reactions at prescribed DOFs (size equal to number of prescribed DOFs)
        """
        K, F = self.assemble_global_stiffness_and_load()
        n = K.shape[0]

        prescribed_dofs = sorted(self.prescribed.keys())
        free_dofs = [i for i in range(n) if i not in self.prescribed]

        d = np.zeros(n, dtype=float)
        if prescribed_dofs:
            d_p = np.array([self.prescribed[i] for i in prescribed_dofs], dtype=float)
        else:
            d_p = np.zeros(0, dtype=float)

        # Partition matrices/vectors
        K_ff = K[np.ix_(free_dofs, free_dofs)]
        K_fp = K[np.ix_(free_dofs, prescribed_dofs)] if prescribed_dofs else np.zeros((len(free_dofs), 0))
        K_pf = K[np.ix_(prescribed_dofs, free_dofs)] if prescribed_dofs else np.zeros((0, len(free_dofs)))
        K_pp = K[np.ix_(prescribed_dofs, prescribed_dofs)] if prescribed_dofs else np.zeros((0, 0))

        F_f = F[free_dofs]
        F_p = F[prescribed_dofs] if prescribed_dofs else np.zeros(0)

        # Solve for free DOFs: K_ff * d_f = F_f - K_fp * d_p
        rhs = F_f - (K_fp @ d_p if d_p.size else 0.0)
        if K_ff.size == 0:
            d_f = np.zeros(0)
        else:
            d_f = np.linalg.solve(K_ff, rhs)
        d[free_dofs] = d_f
        if d_p.size:
            d[prescribed_dofs] = d_p

        # Reactions at prescribed DOFs: r_p = K_pf d_f + K_pp d_p - F_p
        reactions = (K_pf @ d_f) + (K_pp @ d_p if d_p.size else 0.0) - F_p

        return d, F, reactions

    # --- Convenience APIs ---

    def get_node_displacement(self, node_id: int, d: Sequence[float]) -> Tuple[float, float, float]:
        dof_ux, dof_uy, dof_rz = self.dof_indices_for_node(node_id)
        return float(d[dof_ux]), float(d[dof_uy]), float(d[dof_rz])

    def element_end_forces_local(self, elem: BeamElement2D, d: Sequence[float]) -> np.ndarray:
        """Compute element end forces in local coordinates for a given global displacement vector."""
        dofs_i = self.dof_indices_for_node(elem.node_i.id)
        dofs_j = self.dof_indices_for_node(elem.node_j.id)
        edofs = (*dofs_i, *dofs_j)
        d_global = np.array([d[i] for i in edofs], dtype=float)
        T = elem.transformation()
        d_local = T @ d_global  # d_g = T d_l  => d_l = T d_g (consistent with K_g = T^T K_l T)
        k_local = elem.local_stiffness()
        f_local_internal = k_local @ d_local
        # subtract fixed-end forces from distributed loads if any
        f_local = f_local_internal - elem.equivalent_nodal_load_local()
        return f_local


def _cantilever_udl_example() -> None:
    """Run a simple cantilever with UDL example and print results."""
    # Units: N, m
    E = 210e9
    L = 2.0
    b = 0.1
    h = 0.1
    A = b * h
    I = b * h**3 / 12.0
    w = 1000.0  # N/m downward

    model = Beam2DModel()
    n1 = model.add_node(0.0, 0.0)
    n2 = model.add_node(L, 0.0)

    mat = MaterialSection(E, A, I)
    # qy negative => downward in local y (for horizontal element local y = global +y)
    model.add_element(n1, n2, mat, udl_local=DistributedLoadLocal(qx=0.0, qy=-w))

    # Fix cantilever base at node 1
    model.fix_node(n1, ux=True, uy=True, rz=True)

    d, F, reactions = model.solve()

    ux2, uy2, rz2 = model.get_node_displacement(n2, d)

    y_tip_theory = -w * L**4 / (8.0 * E * I)
    theta_tip_theory = -w * L**3 / (6.0 * E * I)

    print("Cantilever with UDL (FEM vs theory):")
    print(f"  Tip uy (FEM)     = {uy2:.6e} m")
    print(f"  Tip uy (theory)  = {y_tip_theory:.6e} m")
    print(f"  Tip rz (FEM)     = {rz2:.6e} rad")
    print(f"  Tip rz (theory)  = {theta_tip_theory:.6e} rad")
    print("  Base reactions [Fx, Fy, Mz] (sign per global):")
    dof_bx, dof_by, dof_bz = model.dof_indices_for_node(n1)
    # reactions are ordered by sorted prescribed dofs; retrieve by index
    prescribed_sorted = sorted(model.prescribed.keys())
    idx_fx = prescribed_sorted.index(dof_bx)
    idx_fy = prescribed_sorted.index(dof_by)
    idx_mz = prescribed_sorted.index(dof_bz)
    print(
        f"    Fx = {reactions[idx_fx]:.3f} N, Fy = {reactions[idx_fy]:.3f} N, Mz = {reactions[idx_mz]:.3f} N·m"
    )


if __name__ == "__main__":
    _cantilever_udl_example()
