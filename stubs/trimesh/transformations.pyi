from _typeshed import Incomplete

__docformat__: str

def identity_matrix(): ...
def translation_matrix(direction): ...
def translation_from_matrix(matrix): ...
def reflection_matrix(point, normal): ...
def reflection_from_matrix(matrix): ...
def rotation_matrix(angle, direction, point: Incomplete | None = ...): ...
def rotation_from_matrix(matrix): ...
def scale_matrix(factor, origin: Incomplete | None = ..., direction: Incomplete | None = ...): ...
def scale_from_matrix(matrix): ...
def projection_matrix(point, normal, direction: Incomplete | None = ..., perspective: Incomplete | None = ..., pseudo: bool = ...): ...
def projection_from_matrix(matrix, pseudo: bool = ...): ...
def clip_matrix(left, right, bottom, top, near, far, perspective: bool = ...): ...
def shear_matrix(angle, direction, point, normal): ...
def shear_from_matrix(matrix): ...
def decompose_matrix(matrix): ...
def compose_matrix(scale: Incomplete | None = ..., shear: Incomplete | None = ..., angles: Incomplete | None = ..., translate: Incomplete | None = ..., perspective: Incomplete | None = ...): ...
def orthogonalization_matrix(lengths, angles): ...
def affine_matrix_from_points(v0, v1, shear: bool = ..., scale: bool = ..., usesvd: bool = ...): ...
def superimposition_matrix(v0, v1, scale: bool = ..., usesvd: bool = ...): ...
def euler_matrix(ai, aj, ak, axes: str = ...): ...
def euler_from_matrix(matrix, axes: str = ...): ...
def euler_from_quaternion(quaternion, axes: str = ...): ...
def quaternion_from_euler(ai, aj, ak, axes: str = ...): ...
def quaternion_about_axis(angle, axis): ...
def quaternion_matrix(quaternion): ...
def quaternion_from_matrix(matrix, isprecise: bool = ...): ...
def quaternion_multiply(quaternion1, quaternion0): ...
def quaternion_conjugate(quaternion): ...
def quaternion_inverse(quaternion): ...
def quaternion_real(quaternion): ...
def quaternion_imag(quaternion): ...
def quaternion_slerp(quat0, quat1, fraction, spin: int = ..., shortestpath: bool = ...): ...
def random_quaternion(rand: Incomplete | None = ..., num: int = ...): ...
def random_rotation_matrix(rand: Incomplete | None = ..., num: int = ...): ...

class Arcball:
    def __init__(self, initial: Incomplete | None = ...) -> None: ...
    def place(self, center, radius) -> None: ...
    def setaxes(self, *axes) -> None: ...
    @property
    def constrain(self): ...
    @constrain.setter
    def constrain(self, value) -> None: ...
    def down(self, point) -> None: ...
    def drag(self, point) -> None: ...
    def next(self, acceleration: float = ...) -> None: ...
    def matrix(self): ...

def arcball_map_to_sphere(point, center, radius): ...
def arcball_constrain_to_axis(point, axis): ...
def arcball_nearest_axis(point, axes): ...
def vector_norm(data, axis: Incomplete | None = ..., out: Incomplete | None = ...): ...
def unit_vector(data, axis: Incomplete | None = ..., out: Incomplete | None = ...): ...
def random_vector(size): ...
def vector_product(v0, v1, axis: int = ...): ...
def angle_between_vectors(v0, v1, directed: bool = ..., axis: int = ...): ...
def inverse_matrix(matrix): ...
def concatenate_matrices(*matrices): ...
def is_same_transform(matrix0, matrix1): ...
def is_same_quaternion(q0, q1): ...
def transform_around(matrix, point): ...
def planar_matrix(offset: Incomplete | None = ..., theta: Incomplete | None = ..., point: Incomplete | None = ..., scale: Incomplete | None = ...): ...
def planar_matrix_to_3D(matrix_2D): ...
def spherical_matrix(theta, phi, axes: str = ...): ...
def transform_points(points, matrix, translate: bool = ...): ...
def is_rigid(matrix, epsilon: float = ...): ...
def scale_and_translate(scale: Incomplete | None = ..., translate: Incomplete | None = ...): ...
def flips_winding(matrix): ...