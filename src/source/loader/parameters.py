from .transform import Transform, p

class Surface(p.PolymorphicStruct):
    transform: Transform

class Circle(Surface, type="circle"):
    pass

class Parameters(p.Struct):
   inner_surface: p.Polymorphic[Surface]
   outer_surface: p.Polymorphic[Surface]