//-zw
// z3dpyfast - The Z3dPy Math Library

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <cmath>


typedef struct {
    double x, y;
} Vector2;

typedef struct {
    double x, y, z;
} Vector3;

typedef struct {
    double x, y, z, w;
} Vector4;

typedef struct {
    double x, y, z;
    Vector2 uv;
} VectorUV;

typedef struct {
    VectorUV p1, p2, p3;
    Vector3 normal, colour, wpos, shade;
    int id;
} Triangle;

typedef struct {
    Vector3 p1, p2, p3;
} BasicTri;

typedef struct {
    float m[4][4];
} Matrix;

Vector3 CamTrg = { 0.f, 0.f, 1.f };
Vector3 CamPos = { 0.f, 0.f, 0.f };

float scrW = 1280.0;
float scrH = 720.0;

//=======================
//     Converter Functions
//=======================


PyObject* Vector3ToPyList(Vector3 inV)
{
    return Py_BuildValue("[fff]", inV.x, inV.y, inV.z);
}

PyObject* Vector4ToPyList(Vector4 inV)
{
    return Py_BuildValue("[ffff]", inV.x, inV.y, inV.z, inV.w);
}

PyObject* VectorUVToPyList(VectorUV inV)
{
    return Py_BuildValue("[fff[fff][ff]]", inV.x, inV.y, inV.z, 0.f, 0.f, 0.f, inV.uv.x, inV.uv.y);
}

Vector2 PyListToVector2(PyObject* inV)
{
    return { PyFloat_AsDouble(PyList_GetItem(inV, 0)),  PyFloat_AsDouble(PyList_GetItem(inV, 1)) };
}

Vector2 PyTupleToVector2(PyObject* inV)
{
    return { PyFloat_AsDouble(PyTuple_GetItem(inV, 0)),  PyFloat_AsDouble(PyTuple_GetItem(inV, 1)) };
}

Vector2 PyVectorToVector2(PyObject* inV)
{
    if (PyList_Check(inV))
        return PyListToVector2(inV);
    return PyTupleToVector2(inV);
}

Vector3 PyListToVector3(PyObject* inLst)
{
    return { PyFloat_AsDouble(PyList_GetItem(inLst, 0)),  PyFloat_AsDouble(PyList_GetItem(inLst, 1)), PyFloat_AsDouble(PyList_GetItem(inLst, 2)) };
}

Vector3 PyTupleToVector3(PyObject* inLst)
{
    return { PyFloat_AsDouble(PyTuple_GetItem(inLst, 0)),  PyFloat_AsDouble(PyTuple_GetItem(inLst, 1)), PyFloat_AsDouble(PyTuple_GetItem(inLst, 2)) };
}

Vector3 PyVectorToVector3(PyObject* inV)
{
    if (PyList_Check(inV))
        return PyListToVector3(inV);
    return PyTupleToVector3(inV);
}

VectorUV PyListToVectorUV(PyObject* inLst)
{
    return { PyFloat_AsDouble(PyList_GetItem(inLst, 0)), PyFloat_AsDouble(PyList_GetItem(inLst, 1)),  PyFloat_AsDouble(PyList_GetItem(inLst, 2)), PyVectorToVector2(PyList_GetItem(inLst, 4)) };
}

VectorUV PyTupleToVectorUV(PyObject* inLst)
{
    return { PyFloat_AsDouble(PyTuple_GetItem(inLst, 0)), PyFloat_AsDouble(PyTuple_GetItem(inLst, 1)),  PyFloat_AsDouble(PyTuple_GetItem(inLst, 2)), PyVectorToVector2(PyTuple_GetItem(inLst, 4)) };
}

VectorUV PyVectorToVectorUV(PyObject* inLst)
{
    if (PyList_Check(inLst))
        return PyListToVectorUV(inLst);
    return PyTupleToVectorUV(inLst);
}

Vector3 VUVToV3(VectorUV v)
{
    return { v.x, v.y, v.z };
}

VectorUV V3ToVUV(Vector3 vec3, float u, float v)
{
    return { vec3.x, vec3.y, vec3.z, { u, v } };
}

Triangle PyListToTri(PyObject* tri)
{
    return { PyVectorToVectorUV(PyList_GetItem(tri, 0)), PyVectorToVectorUV(PyList_GetItem(tri, 1)), PyVectorToVectorUV(PyList_GetItem(tri, 2)), PyVectorToVector3(PyList_GetItem(tri, 3)), PyVectorToVector3(PyList_GetItem(tri, 4)), PyVectorToVector3(PyList_GetItem(tri, 5)), PyVectorToVector3(PyList_GetItem(tri, 6)), PyLong_AsLong(PyList_GetItem(tri, 7)) };
}

Triangle PyTupleToTri(PyObject* tri)
{
    return { PyVectorToVectorUV(PyTuple_GetItem(tri, 0)), PyVectorToVectorUV(PyTuple_GetItem(tri, 1)), PyVectorToVectorUV(PyTuple_GetItem(tri, 2)), PyVectorToVector3(PyTuple_GetItem(tri, 3)), PyVectorToVector3(PyTuple_GetItem(tri, 4)), PyVectorToVector3(PyTuple_GetItem(tri, 5)), PyVectorToVector3(PyTuple_GetItem(tri, 6)), PyLong_AsLong(PyTuple_GetItem(tri, 7)) };
}

Triangle PyTriToCTri(PyObject* tri)
{
    if (PyList_Check(tri))
        return PyListToTri(tri);
    return PyTupleToTri(tri);
}

PyObject* TriToPyList(Triangle inTri)
{
    return Py_BuildValue("[OOO[fff][fff][fff][iii]i]", VectorUVToPyList(inTri.p1), VectorUVToPyList(inTri.p2), VectorUVToPyList(inTri.p3), inTri.normal.x, inTri.normal.y, inTri.normal.z, inTri.wpos.x, inTri.wpos.y, inTri.wpos.z, inTri.shade.x, inTri.shade.y, inTri.shade.z, inTri.colour.x, inTri.colour.y, inTri.colour.z, inTri.id);
}

Vector3 Vector4ToVector3(Vector4 v)
{
    return { v.x, v.y, v.z };
}


//=======================
//     Vector3 Functions
//=======================


Vector3 VectorAdd(Vector3 v1, Vector3 v2)
{
    return { v1.x + v2.x, v1.y + v2.y, v1.z + v2.z };
}

Vector3 VectorSub(Vector3 v1, Vector3 v2)
{
    return { v1.x - v2.x, v1.y - v2.y, v1.z - v2.z };
}

Vector3 VectorMul(Vector3 v1, Vector3 v2)
{
    return { v1.x * v2.x, v1.y * v2.y, v1.z * v2.z };
}

Vector3 VectorMulF(Vector3 v1, float f)
{
    return { v1.x * f, v1.y * f, v1.z * f };
}

float VectorDoP(Vector3 v1, Vector3 v2)
{
    return (v1.x * v2.x) + (v1.y * v2.y) + (v1.z * v2.z);
}

Vector3 VectorCrP(Vector3 v1, Vector3 v2)
{
    return { (v1.y * v2.z) - (v1.z * v2.y), (v1.z * v2.x) - (v1.x * v2.z), (v1.x * v2.y) - (v1.y * v2.x) };
}

float VectorGetLength(Vector3 v)
{
    return sqrtf((v.x * v.x) + (v.y * v.y) + (v.z * v.z));
}

Vector3 VectorNormalize(Vector3 v)
{
    float l = fabs(VectorGetLength(v));
    if (l != 0.f)
    {
        return { v.x / l, v.y / l, v.z / l };
    }
    return { v.x, v.y, v.z };
}

float DistanceBetweenVectors(Vector3 v1, Vector3 v2)
{
    float x = (v2.x - v1.x);
    float y = (v2.y - v1.y);
    float z = (v2.z - v1.z);
    return sqrtf((x * x) + (y * y) + (z * z));
}

Vector3 DirectionBetweenVectors(Vector3 v1, Vector3 v2)
{
    return VectorNormalize(VectorSub(v2, v1));
}


void WrapRot(Vector3* rot)
{
    while (rot->x < 0.0)
        rot->x += 360.0;
    while (rot->y < 0.0)
        rot->y += 360.0;
    while (rot->z < 0.0)
        rot->z += 360.0;

    rot->x = fmod(rot->x, 360.f);
    rot->y = fmod(rot->y, 360.f);
    rot->z = fmod(rot->z, 360.f);
}




//=======================
//     Vector UV Functions
//=======================


VectorUV VectorUVAdd(VectorUV v1, Vector3 v2)
{
    return { v1.x + v2.x, v1.y + v2.y, v1.z + v2.z, v1.uv };
}

VectorUV VectorUVSub(VectorUV v1, Vector3 v2)
{
    return { v1.x - v2.x, v1.y - v2.y, v1.z - v2.z, v1.uv };
}

VectorUV VectorUVDiv(VectorUV v1, Vector3 v2)
{
    return { v1.x / v2.x, v1.y / v2.y, v1.z / v2.z, v1.uv };
}

VectorUV VectorUVDivF(VectorUV v1, float f)
{
    return { v1.x / f, v1.y / f, v1.z / f, v1.uv };
}

VectorUV VectorUVMul(VectorUV v1, Vector3 v2)
{
    return { v1.x * v2.x, v1.y * v2.y, v1.z * v2.z, v1.uv };
}

VectorUV VectorUVMulF(VectorUV in, float f)
{
    return { in.x * f, in.y * f, in.z * f, in.uv };
}


//=======================
//     Triangle Functions
//=======================


Vector3 TriangleAverage(Triangle tri)
{
    return { (tri.p1.x + tri.p2.x + tri.p3.x) * 0.333333f, (tri.p1.y + tri.p2.y + tri.p3.y) * 0.333333f, (tri.p1.z + tri.p2.z + tri.p3.z) * 0.333333f };
}

Vector3 GetNormal(BasicTri tri)
{
    Vector3 line1 = VectorSub(tri.p2, tri.p1);
    Vector3 line2 = VectorSub(tri.p3, tri.p1);
    return VectorMul(VectorNormalize(VectorCrP(line1, line2)), { 1.0, -1.0, -1.0 });
}

Vector3 VectorIntersectPlane(Vector3 pPos, Vector3 pNrm, Vector3 lSta, Vector3 lEnd)
{
    pNrm = VectorNormalize(pNrm);
    double plane_d = -VectorDoP(pNrm, pPos);
    double ad = VectorDoP(lSta, pNrm);
    double bd = VectorDoP(lEnd, pNrm);
    double t = (-plane_d - ad) / (bd - ad);
    Vector3 lineStartToEnd = VectorSub(lEnd, lSta);
    Vector3 lineToIntersect = VectorMulF(lineStartToEnd, t);
    return VectorAdd(lSta, lineToIntersect);
}

VectorUV VectorUVIntersectPlane(Vector3 pPos, Vector3 pNrm, VectorUV lSta, VectorUV lEnd)
{
    pNrm = VectorNormalize(pNrm);
    double plane_d = -VectorDoP(pNrm, pPos);
    double ad = VectorDoP(VUVToV3(lSta), pNrm);
    double bd = VectorDoP(VUVToV3(lEnd), pNrm);
    double t = (-plane_d - ad) / (bd - ad);
    VectorUV lineStartToEnd = VectorUVSub(lEnd, VUVToV3(lSta));
    VectorUV lineToIntersect = VectorUVMulF(lineStartToEnd, t);
    lineToIntersect.uv = { (lEnd.uv.x - lSta.uv.x) * t + lSta.uv.x, (lEnd.uv.y - lSta.uv.y) * t + lSta.uv.y};
    return VectorUVAdd(lineToIntersect, VUVToV3(lSta));
}

float ShortestPointToPlane(Vector3 point, Vector3 plNrm, Vector3 plPos)
{
    return VectorDoP(plNrm, point) - VectorDoP(plNrm, plPos);
}


//=======================
//     Matrix Functions
//=======================


Matrix TemplateMatrix()
{
    Matrix output;
    for (int x = 0; x < 4; x++)
    {
        for (int y = 0; y < 4; y++)
        {
            output.m[x][y] = 0.0;
        }
    }
    return output;
}

Matrix MakeRotMatX(float deg)
{
    float rad = deg * 0.0174533f;
    Matrix output = TemplateMatrix();
    output.m[0][0] = 1.0;
    output.m[1][1] = cosf(rad);
    output.m[1][2] = sinf(rad);
    output.m[2][1] = -sinf(rad);
    output.m[2][2] = cosf(rad);
    output.m[3][3] = 1.0;
    return output;
}

Matrix MakeRotMatY(float deg)
{
    float rad = deg * 0.0174533f;
    Matrix output = TemplateMatrix();
    output.m[0][0] = cosf(rad);
    output.m[0][2] = sinf(rad);
    output.m[1][1] = 1.0;
    output.m[2][0] = -sinf(rad);
    output.m[2][2] = cosf(rad);
    output.m[3][3] = 1.0;
    return output;
}

Matrix MakeRotMatZ(float deg)
{
    float rad = deg * 0.0174533f;
    Matrix output = TemplateMatrix();
    output.m[0][0] = cosf(rad);
    output.m[0][1] = sinf(rad);
    output.m[1][0] = -sinf(rad);
    output.m[1][1] = cosf(rad);
    output.m[2][2] = 1.0;
    output.m[3][3] = 1.0;
    return output;
}

BasicTri MatrixStuff(Vector3 pos, Vector3 target, Vector3 up)
{
    Vector3 newFwd = VectorSub(target, pos);
    newFwd = VectorNormalize(newFwd);

    Vector3 a = VectorMulF(newFwd, VectorDoP(up, newFwd));
    Vector3 newUp = VectorSub(up, a);
    newUp = VectorNormalize(newUp);

    Vector3 newRght = VectorCrP(newUp, newFwd);
    return { newFwd, newUp, newRght };
}

Matrix MatrixMatrixMul(Matrix m1, Matrix m2)
{
    Matrix output = TemplateMatrix();
    for (int x = 0; x < 4; x++)
    {
        for (int y = 0; y < 4; y++)
        {
            output.m[y][x] = m1.m[y][0] * m2.m[0][x] + m1.m[y][1] * m2.m[1][x] + m1.m[y][2] * m2.m[2][x] + m1.m[y][3] * m2.m[3][x];
        }
    }
    return output;
}

Vector3 Vector3MatrixMul(Vector3 v, Matrix m)
{
    Vector3 output;
    output.x = v.x * m.m[0][0] + v.y * m.m[1][0] + v.z * m.m[2][0] + m.m[3][0];
    output.y = v.x * m.m[0][1] + v.y * m.m[1][1] + v.z * m.m[2][1] + m.m[3][1];
    output.z = v.x * m.m[0][2] + v.y * m.m[1][2] + v.z * m.m[2][2] + m.m[3][2];
    float w = v.x * m.m[0][3] + v.y * m.m[1][3] + v.z * m.m[2][3] + m.m[3][3];
    if (w != 0.0)
        return { output.x / w, output.y / w, output.z / w };
    return output;
}

VectorUV VectorUVMatrixMul(VectorUV v, Matrix m)
{
    Vector3 result = Vector3MatrixMul({ v.x, v.y, v.z }, m);
    return { result.x, result.y, result.z, v.uv };
}

Triangle TriMatrixMul(Triangle tri, Matrix m)
{
    return { VectorUVMatrixMul(tri.p1, m), VectorUVMatrixMul(tri.p2, m), VectorUVMatrixMul(tri.p3, m), tri.normal, tri.wpos, tri.shade };
}

Vector3 VectorRotateX(Vector3 v, float deg)
{
    return Vector3MatrixMul(v, MakeRotMatX(deg));
}

Vector3 VectorRotateY(Vector3 v, float deg)
{
    return Vector3MatrixMul(v, MakeRotMatY(deg));
}

Vector3 VectorRotateZ(Vector3 v, float deg)
{
    return Vector3MatrixMul(v, MakeRotMatZ(deg));
}

Vector3 RotTo(Vector3 rot, Vector3 target)
{
    WrapRot(&rot);
    Vector3 output = VectorRotateX(target, rot.x);
    output = VectorRotateZ(output, rot.z);
    return VectorRotateY(output, rot.y);
}

Vector3 CheapLighting(Triangle tri, PyObject* lights)
{
    float shading = 0.f;
    Vector3 colour = { 0.0, 0.0, 0.0 };
    float intensity = 0.f;
    Vector3 nNormal = VectorMul(tri.normal, { -1, 1, 1 });
    Vector3 pos = tri.wpos;
    PyObject* light;
    int num = 0;
    Py_ssize_t size = PyList_GET_SIZE(lights);
    for (Py_ssize_t l = 0; l < size; l++)
    {
        light = PyList_GetItem(lights, l);
        Vector3 lpos = PyVectorToVector3(PyList_GetItem(light, 1));
        float radius = PyFloat_AsDouble(PyList_GetItem(light, 3));
        float dist = DistanceBetweenVectors(pos, lpos);
        if (dist <= radius)
        {
            Vector3 lightDir = DirectionBetweenVectors(lpos, pos);
            float dot = VectorDoP(lightDir, nNormal);
            if (dot > 0)
            {
                float d = dist / radius;
                intensity = (1 - (d * d)) * PyFloat_AsDouble(PyList_GetItem(light, 2));
                shading += dot;
            }
        }
    }
}


//=======================
//     Python Entrypoints
//=======================


PyObject* CShortestPointToPlane(PyObject* self, PyObject* args)
{
    PyObject* pythonPoint, * pythonNrm, * pythonPos;
    if (!PyArg_ParseTuple(args, "OOO", &pythonPoint, &pythonNrm, &pythonPos))
        return NULL;
    Vector3 nrm = PyVectorToVector3(pythonNrm);

    return PyFloat_FromDouble(ShortestPointToPlane(PyVectorToVector3(pythonPoint), nrm, PyVectorToVector3(pythonPos)));
}

PyObject* CVectorIntersectPlane(PyObject* self, PyObject* args)
{
    PyObject* inPos, * inNrm, * inSta, * inEnd;
    if (!PyArg_ParseTuple(args, "OOOO", &inPos, &inNrm, &inSta, &inEnd))
        return NULL;

    return Vector3ToPyList(VectorIntersectPlane(PyVectorToVector3(inPos), PyVectorToVector3(inNrm), PyVectorToVector3(inSta), PyVectorToVector3(inEnd)));
}

PyObject* CDistanceBetweenVectors(PyObject* self, PyObject* args)
{
    PyObject* v1, * v2;
    if (!PyArg_ParseTuple(args, "OO", &v1, &v2))
        return NULL;

    return PyFloat_FromDouble(DistanceBetweenVectors(PyVectorToVector3(v1), PyVectorToVector3(v2)));
}

PyObject* CDirectionBetweenVectors(PyObject* self, PyObject* args)
{
    PyObject* v1, * v2;
    if (!PyArg_ParseTuple(args, "OO", &v1, &v2))
        return NULL;

    return Vector3ToPyList(DirectionBetweenVectors(PyVectorToVector3(v1), PyVectorToVector3(v2)));
}

PyObject* CRotTo(PyObject* self, PyObject* args)
{
    PyObject* rot, * trg;
    if (!PyArg_ParseTuple(args, "OO", &rot, &trg))
        return NULL;

    return Vector3ToPyList(RotTo(PyVectorToVector3(rot), PyVectorToVector3(trg)));
}

PyObject* CVectorUVIntersectPlane(PyObject* self, PyObject* args)
{
    PyObject* pos, * nrm, * sta, * end;
    if (!PyArg_ParseTuple(args, "OOOO", &pos, &nrm, &sta, &end))
        return NULL;

    return VectorUVToPyList(VectorUVIntersectPlane(PyVectorToVector3(pos), PyVectorToVector3(nrm), PyVectorToVectorUV(sta), PyVectorToVectorUV(end)));
}

PyObject* CMatrixStuff(PyObject* self, PyObject* args)
{
    PyObject* pos, * target, * up;
    if (!PyArg_ParseTuple(args, "OOO", &pos, &target, &up))
        return NULL;
    BasicTri output = MatrixStuff(PyVectorToVector3(pos), PyVectorToVector3(target), PyVectorToVector3(up));
    return Py_BuildValue("[[fff][fff][fff]]", output.p1.x, output.p1.y, output.p1.z, output.p2.x, output.p2.y, output.p2.z, output.p3.x, output.p3.y, output.p3.z);
}

PyObject* CGetNormal(PyObject* self, PyObject* args)
{
    PyObject* tri;
    if (!PyArg_ParseTuple(args, "O", &tri))
        return NULL;

    return Vector3ToPyList(GetNormal({ PyVectorToVector3(PyList_GetItem(tri, 0)), PyVectorToVector3(PyList_GetItem(tri, 1)), PyVectorToVector3(PyList_GetItem(tri, 2)) }));
}


//=======================
//     Python Stuff
//=======================


static PyMethodDef z3dpyfast_methods[] = {
    { "DistanceBetweenVectors", (PyCFunction)CDistanceBetweenVectors, METH_VARARGS, nullptr },
    { "DirectionBetweenVectors", (PyCFunction)CDirectionBetweenVectors, METH_VARARGS, nullptr },
    { "ShortestPointToPlane", (PyCFunction)CShortestPointToPlane, METH_VARARGS, nullptr },
    { "VectorUVIntersectPlane", (PyCFunction)CVectorUVIntersectPlane, METH_VARARGS, nullptr },
    { "RotTo", (PyCFunction)CRotTo, METH_VARARGS, nullptr },
    { "GetNormal", (PyCFunction)CGetNormal, METH_VARARGS, nullptr },
    { "MatrixStuff", (PyCFunction)CMatrixStuff, METH_VARARGS, nullptr },
    { nullptr, nullptr, 0, nullptr }
};

static PyModuleDef z3dpyfast_module = {
    PyModuleDef_HEAD_INIT,
    "z3dpyfast",
    "Core Z3dPy functions re-written in C++ for speed.",
    0,
    z3dpyfast_methods
};

PyMODINIT_FUNC PyInit_z3dpyfast(void) {
    return PyModule_Create(&z3dpyfast_module);
}

int main(int argc, char* argv[])
{
    wchar_t* program = Py_DecodeLocale(argv[0], NULL);
    if (program == NULL) {
        fprintf(stderr, "Fatal error: cannot decode argv[0]\n");
        exit(1);
    }

    /* Add a built-in module, before Py_Initialize */
    if (PyImport_AppendInittab("z3dpyfast", PyInit_z3dpyfast) == -1) {
        fprintf(stderr, "Error: could not extend in-built modules table\n");
        exit(1);
    }

    /* Initialize the Python interpreter.  Required.
       If this step fails, it will be a fatal error. */
    Py_Initialize();

    /* Optionally import the module; alternatively,
       import can be deferred until the embedded script
       imports it. */
    PyObject* pmodule = PyImport_ImportModule("z3dpyfast");
    if (!pmodule) {
        PyErr_Print();
        fprintf(stderr, "Error: could not import module 'z3dpyfast'\n");
    }

    PyMem_RawFree(program);
    return 0;
}