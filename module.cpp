// Z3dPy C++ Extension To Speed Up Python, Because Python Is Unfortunately Way Too Slow
// or ZPC++ETSUPBPIUWTS for short
// I was originally going to write it in C, but C doesn't have <vector> so...

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <cmath>
#include <iostream>
#include <fstream>
#include <vector>
#include <sstream>
#include <windows.h>


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
    double x, y, z, u, v;
} VectorUV;

typedef struct {
    VectorUV p1, p2, p3;
    Vector3 normal, colour, wpos;
    double shade;
    int id;
} Triangle;

typedef struct {
    Vector3 p1, p2, p3;
} BasicTri;

typedef struct {
    std::vector <Triangle> tris;
} Mesh;


typedef struct {
    std::vector<Mesh> meshes;
} Thing;

typedef struct {
    double m[4][4];
} Matrix;

typedef struct {
    Vector3 pos, colour;
    float strength, radius;
    int intId;
} Light_Point;

std::vector<Light_Point> lights = {};

Vector3 CamTrg = { 0.f, 0.f, 1.f };
Vector3 CamPos = { 0.f, 0.f, 0.f };

// So here's the plan.
// Python gives C++ the position and rotation as variables during raster,
// so only the meshes need to be stored, and Python can pass an index instead of
// an entire list of triangles.
std::vector<Thing> things = {};

static Vector3 VectorAdd(Vector3 v1, Vector3 v2)
{
    return { v1.x + v2.x, v1.y + v2.y, v1.z + v2.z };
}

static VectorUV VectorUVAdd(VectorUV v1, Vector3 v2)
{
    return { v1.x + v2.x, v1.y + v2.y, v1.z + v2.z, v1.u, v1.v };
}

static Vector3 VectorSub(Vector3 v1, Vector3 v2)
{
    return { v1.x - v2.x, v1.y - v2.y, v1.z - v2.z };
}

static Vector3 VectorMul(Vector3 v1, Vector3 v2)
{
    return { v1.x * v2.x, v1.y * v2.y, v1.z * v2.z };
}

static Vector3 VectorMulF(Vector3 v1, float f)
{
    return { v1.x * f, v1.y * f, v1.z * f };
}

static double VectorDoP(Vector3 v1, Vector3 v2)
{
    return (v1.x * v2.x) + (v1.y * v2.y) + (v1.z * v1.z);
}

static Vector3 VectorCrP(Vector3 v1, Vector3 v2)
{
    return { (v1.y * v2.z) - (v1.z * v1.y), (v1.z * v2.x) - (v1.x * v2.z), (v1.x * v2.y) - (v1.y * v2.x) };
}

// Converter Functions

static PyObject* Vector3ToPyList(Vector3 inV)
{
    PyObject* outV = PyList_New(3);
    PyList_SetItem(outV, 0, PyFloat_FromDouble(inV.x));
    PyList_SetItem(outV, 1, PyFloat_FromDouble(inV.y));
    PyList_SetItem(outV, 2, PyFloat_FromDouble(inV.z));
    return outV;
}

static PyObject* Vector4ToPyList(Vector4 inV)
{
    PyObject* outV = PyList_New(4);
    PyList_SetItem(outV, 0, PyFloat_FromDouble(inV.x));
    PyList_SetItem(outV, 1, PyFloat_FromDouble(inV.y));
    PyList_SetItem(outV, 2, PyFloat_FromDouble(inV.z));
    PyList_SetItem(outV, 3, PyFloat_FromDouble(inV.w));
    return outV;
}

static PyObject* VectorUVToPyList(VectorUV inV)
{
    PyObject* outV = PyList_New(5);
    PyObject* UV = PyList_New(2);
    PyList_SetItem(outV, 0, PyFloat_FromDouble(inV.x));
    PyList_SetItem(outV, 1, PyFloat_FromDouble(inV.y));
    PyList_SetItem(outV, 2, PyFloat_FromDouble(inV.z));
    PyList_SetItem(outV, 3, Py_BuildValue("[fff]", 0.f, 0.f, 0.f));
    PyList_SetItem(UV, 0, PyFloat_FromDouble(inV.u));
    PyList_SetItem(UV, 1, PyFloat_FromDouble(inV.v));
    PyList_SetItem(outV, 4, UV);
    return outV;
}

static Vector3 PyVectorToVector3(PyObject* inLst)
{
    return { PyFloat_AsDouble(PyList_GetItem(inLst, 0)),  PyFloat_AsDouble(PyList_GetItem(inLst, 1)), PyFloat_AsDouble(PyList_GetItem(inLst, 2)) };
}

static VectorUV PyVectorToVectorUV(PyObject* inLst)
{
    VectorUV output;
    output.x = PyFloat_AsDouble(PyList_GetItem(inLst, 0));
    output.y = PyFloat_AsDouble(PyList_GetItem(inLst, 1));
    output.z = PyFloat_AsDouble(PyList_GetItem(inLst, 2));
    output.u = PyFloat_AsDouble(PyList_GetItem(PyList_GetItem(inLst, 4), 0));
    output.v = PyFloat_AsDouble(PyList_GetItem(PyList_GetItem(inLst, 4), 1));
    return output;
}

static Vector3 VUVToV3(VectorUV v)
{
    return { v.x, v.y, v.z };
}

static VectorUV V3ToVUV(Vector3 vec3, double u, double v)
{
    return { vec3.x, vec3.y, vec3.z, u, v };
}

static Triangle PyTriToCTri(PyObject* tri)
{
    return { PyVectorToVectorUV(PyList_GetItem(tri, 0)), PyVectorToVectorUV(PyList_GetItem(tri, 1)), PyVectorToVectorUV(PyList_GetItem(tri, 2)), PyVectorToVector3(PyList_GetItem(tri, 3)), PyVectorToVector3(PyList_GetItem(tri, 4)), PyFloat_AsDouble(PyList_GetItem(tri, 5)) };
}

static double VectorGetLength(Vector3 v)
{
    return sqrt((v.x * v.x) + (v.y * v.y) + (v.z * v.z));
}

static Vector3 VectorNormalize(Vector3 v)
{
    float l = abs(VectorGetLength(v));
    if (l != 0.f)
    {
        return { v.x / l, v.y / l, v.z / l };
    }
    return v;
}

static float DistanceBetweenVectors(Vector3 v1, Vector3 v2)
{
    double x = (v2.x - v1.x) * (v2.x - v1.x);
    double y = (v2.y - v1.y) * (v2.y - v1.y);
    double z = (v2.z - v1.z) * (v2.z - v1.z);
    return sqrtf(x + y + z);
}

static Vector3 DirectionBetweenVectors(Vector3 v1, Vector3 v2)
{
    return VectorNormalize(VectorSub(v2, v1));
}

Vector3 TriangleAverage(Triangle tri)
{
    return { (tri.p1.x + tri.p2.x + tri.p3.x) * 0.333333, (tri.p1.y + tri.p2.y + tri.p3.y) * 0.333333, (tri.p1.z + tri.p2.z + tri.p3.z) * 0.333333 };
}

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

Matrix MakeRotMatX(double deg)
{
    double rad = deg * 0.0174533;
    Matrix output = TemplateMatrix();
    output.m[0][0] = 1.0;
    output.m[1][1] = cosf(rad);
    output.m[1][2] = sinf(rad);
    output.m[2][1] = -sinf(rad);
    output.m[2][2] = cosf(rad);
    output.m[3][3] = 1.0;
    return output;
}

Matrix MakeRotMatY(double deg)
{
    double rad = deg * 0.0174533;
    Matrix output = TemplateMatrix();
    output.m[0][0] = cosf(rad);
    output.m[0][2] = sinf(rad);
    output.m[1][1] = 1.0;
    output.m[2][0] = -sinf(rad);
    output.m[2][2] = cosf(rad);
    output.m[3][3] = 1.0;
    return output;
}

Matrix MakeRotMatZ(double deg)
{
    double rad = deg * 0.0174533;
    Matrix output = TemplateMatrix();
    output.m[0][0] = cosf(rad);
    output.m[0][1] = sinf(rad);
    output.m[1][0] = -sinf(rad);
    output.m[1][1] = cosf(rad);
    output.m[2][2] = 1.0;
    output.m[3][3] = 1.0;
    return output;
}

static void ThingsRemoveItem(int index)
{
    int size = (int)things.size();
    std::vector<Thing> nT;
    for (int t = 0; t < things.size(); t++)
    {
        if (t != index)
            nT.push_back(things[t]);
    }
    things = nT;
}

BasicTri MatrixStuff(Vector3 pos, Vector3 target, Vector3 up)
{
    BasicTri output;
    Vector3 newFwd = VectorSub(target, pos);
    newFwd = VectorNormalize(newFwd);
    

    Vector3 a = VectorMulF(newFwd, VectorDoP(up, newFwd));
    Vector3 newUp = VectorSub(up, a);
    newUp = VectorNormalize(newUp);

    Vector3 newRght = VectorCrP(newUp, newFwd);
    
    output.p1 = newFwd;
    output.p2 = newUp;
    output.p3 = newRght;
    return output;
}

Matrix MakeLookMat(Vector3 pos, Vector3 target, Vector3 up)
{
    Matrix output = TemplateMatrix();
    BasicTri temp = MatrixStuff(pos, target, up);
    output.m[0][0] = temp.p3.x;
    output.m[0][1] = temp.p2.x;
    output.m[0][2] = temp.p1.x;
    output.m[1][0] = temp.p3.y;
    output.m[1][1] = temp.p2.y;
    output.m[1][2] = temp.p1.y;
    output.m[2][0] = temp.p3.z;
    output.m[2][1] = temp.p2.z;
    output.m[2][2] = temp.p1.z;
    output.m[3][0] = -VectorDoP(pos, temp.p3);
    output.m[3][1] = -VectorDoP(pos, temp.p2);
    output.m[3][2] = -VectorDoP(pos, temp.p1);
    output.m[3][3] = 1.0;
    return output;
}

Matrix matV = MakeLookMat(CamPos, CamTrg, { 0.f, 1.f, 0.f });

static Matrix MatrixMatrixMul(Matrix m1, Matrix m2)
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

Vector3 Vector4ToVector3(Vector4 v)
{
    Vector3 output;
    output.x = v.x;
    output.y = v.y;
    output.z = v.z;
    return output;
}

Vector3 Vector3MatrixMul(Vector3 v, Matrix m)
{
    Vector4 output;
    output.x = v.x * m.m[0][0] + v.y * m.m[1][0] + v.z * m.m[2][0] + m.m[3][0];
    output.y = v.x * m.m[0][1] + v.y * m.m[1][1] + v.z * m.m[2][1] + m.m[3][1];
    output.z = v.x * m.m[0][2] + v.y * m.m[1][2] + v.z * m.m[2][2] + m.m[3][2];
    output.w = v.x * m.m[0][3] + v.y * m.m[1][3] + v.z * m.m[2][3] + m.m[3][3];
    return Vector4ToVector3(output);
}

VectorUV VectorUVMatrixMul(VectorUV v, Matrix m)
{
    VectorUV output;
    Vector3 basic;
    basic.x = v.x;
    basic.y = v.y;
    basic.z = v.z;
    Vector3 result = Vector3MatrixMul(basic, m);
    output.x = result.x;
    output.y = result.y;
    output.z = result.z;
    output.u = v.u;
    output.v = v.v;
    return output;
}

static Triangle TriangleAdd(Triangle tri, Vector3 pos)
{
    Triangle output;
    output.p1 = VectorUVAdd(tri.p1, pos);
    output.p2 = VectorUVAdd(tri.p2, pos);
    output.p3 = VectorUVAdd(tri.p3, pos);
    output.normal = tri.normal;
    output.wpos = tri.wpos;
    output.shade = tri.shade;
    return output;
}

// Modifies the input vector of triangles.
static std::vector<Triangle> TranslateTriangles(std::vector <Triangle> inTris, Vector3 pos)
{
    Triangle ntri;
    std::vector<Triangle> output;
    for (const Triangle tri : inTris)
    {
        ntri = TriangleAdd(tri, pos);
        ntri.wpos = TriangleAverage(tri);
        output.push_back(ntri);
    }
    return output;
}

static Triangle TriMatrixMul(Triangle tri, Matrix m)
{
    Triangle output;
    output.p1 = VectorUVMatrixMul(tri.p1, m);
    output.p2 = VectorUVMatrixMul(tri.p2, m);
    output.p3 = VectorUVMatrixMul(tri.p3, m);
    output.normal = tri.normal;
    output.shade = tri.shade;
    output.wpos = tri.wpos;
    return output;
}

static Vector3 GetNormal(Triangle tri)
{
    Vector3 that = { 0.f, 0.f, 0.f };
    Vector3 output, line1, line2;
    line1.x = tri.p2.x - tri.p1.x;
    line1.y = tri.p2.y - tri.p1.y;
    line1.z = tri.p2.z - tri.p1.z;
    line2.x = tri.p3.x - tri.p1.x;
    line2.y = tri.p3.y - tri.p1.y;
    line2.z = tri.p3.z - tri.p1.z;
    output = VectorCrP(line1, line2);
    return VectorMul(VectorNormalize(output), { 1.f, -1.f, -1.f });
}

// Raster Functions

// Returns a new vector of triangles.
static std::vector <Triangle> TransformTriangles(std::vector <Triangle> tris, Vector3 rot, Vector3 camTrg)
{
    Triangle f;
    std::vector <Triangle> output;
    Matrix mw = MakeRotMatX(rot.x);
    mw = MatrixMatrixMul(mw, MakeRotMatY(rot.y));
    mw = MatrixMatrixMul(mw, MakeRotMatZ(rot.z));
    for (const Triangle tri : tris)
    {
        f = TriMatrixMul(tri, mw);
        f.normal = GetNormal(f);
        f.colour = tri.colour;
        output.push_back(f);
    }
    return output;
}

static Triangle TransformTriangle(Triangle tri, Matrix matrix)
{
    Triangle output = TriMatrixMul(tri, matrix);
    output.normal = GetNormal(output);
    output.colour = tri.colour;
    return output;
}

static std::vector<Triangle> ViewTriangles(std::vector<Triangle> tris, Vector3 pos, Vector3 target)
{
    std::vector<Triangle> output;
    for (const Triangle tri : tris)
    {
        output.push_back(TriMatrixMul(tri, matV));
    }
    return output;
}

static Triangle ViewTriangle(Triangle tri, Matrix m)
{
    return TriMatrixMul(tri, m);
}

static Vector3 VectorIntersectPlane(Vector3 pPos, Vector3 pNrm, Vector3 lSta, Vector3 lEnd)
{
    pNrm = VectorNormalize(pNrm);
    float plane_d = -VectorDoP(pNrm, pPos);
    float ad = VectorDoP(lSta, pNrm);
    float bd = VectorDoP(lEnd, pNrm);
    float t = (-plane_d - ad) / (bd - ad);
    Vector3 lineStartToEnd = VectorSub(lEnd, lSta);
    Vector3 lineToIntersect = VectorMulF(lineStartToEnd, t);
    return VectorAdd(lSta, lineToIntersect);
}

static float ShortestPointToPlane(Vector3 point, Vector3 plNrm, Vector3 plPos)
{
    return VectorDoP(plNrm, point) - VectorDoP(plNrm, plPos);
}

double scrW = 1280.0;
double scrH = 720.0;

static std::vector<Triangle> TriClipAgainstPlane(Triangle tri, Vector3 pPos, Vector3 pNrm)
{
    pNrm = VectorNormalize(pNrm);
    std::vector<VectorUV> insideP, outsideP;
    float d1 = ShortestPointToPlane(VUVToV3(tri.p1), pNrm, pPos);
    float d2 = ShortestPointToPlane(VUVToV3(tri.p2), pNrm, pPos);
    float d3 = ShortestPointToPlane(VUVToV3(tri.p3), pNrm, pPos);

    if (d1 >= 0)
        insideP.push_back(tri.p1);
    else
        outsideP.push_back(tri.p1);
    if (d2 >= 0)
        insideP.push_back(tri.p2);
    else
        outsideP.push_back(tri.p2);
    if (d3 >= 0)
        insideP.push_back(tri.p3);
    else
        outsideP.push_back(tri.p3);
    
    int iS = insideP.size();
    int oS = outsideP.size();
    if (iS == 0)
        return {  };

    if (iS == 3)
        return { tri };

    if (iS == 1 && oS == 2)
    {
        Triangle t1;
        t1.p1 = insideP[0];
        t1.p2 = V3ToVUV(VectorIntersectPlane(pPos, pNrm, VUVToV3(insideP[0]), VUVToV3(outsideP[1])), tri.p2.u, tri.p2.v);
        t1.p3 = V3ToVUV(VectorIntersectPlane(pPos, pNrm, VUVToV3(insideP[0]), VUVToV3(outsideP[0])), tri.p3.u, tri.p3.v);
        t1.normal = tri.normal;
        t1.wpos = tri.wpos;
        t1.shade = tri.shade;
        return { t1 };
    }

    if (iS == 2 && oS == 1)
    {
        Triangle t1, t2;
        t1.p1 = insideP[0];
        t1.p2 = insideP[1];
        t1.p3 = V3ToVUV(VectorIntersectPlane(pPos, pNrm, VUVToV3(insideP[1]), VUVToV3(outsideP[0])), tri.p3.u, tri.p3.v);
        t2.p1 = insideP[0];
        t2.p2 = t1.p3;
        t2.p3 = V3ToVUV(VectorIntersectPlane(pPos, pNrm, VUVToV3(insideP[0]), VUVToV3(outsideP[0])), tri.p3.u, tri.p3.v);

        t1.normal = tri.normal;
        t1.shade = tri.shade;
        t2.normal = tri.normal;
        t2.shade = tri.shade;
        t1.wpos = tri.wpos;
        t2.wpos = tri.wpos;
        return { t1, t2 };
    }
    return {  };
}

static std::vector<Triangle> TriClipAgainstScreenEdges(Triangle tri)
{
    std::vector<Triangle> output;
    for (const Triangle t : TriClipAgainstPlane(tri, { 0.0, 0.0, 0.0 }, { 0.0, 1.0, 0.0 }))
        for (const Triangle r : TriClipAgainstPlane(t, { 0.0,  scrH - 1, 0.0 }, { 0.0, -1.0, 0.0 }))
            for (const Triangle i : TriClipAgainstPlane(r, { 0.0, 0.0, 0.0 }, { 1.0, 0.0, 0.0 }))
                for (const Triangle s : TriClipAgainstPlane(i, { scrW - 1,  0.0, 0.0 }, { -1.0, 0.0, 0.0 }))
                    output.push_back(s);
    return output;
}

static PyObject* CTriClipAgainstScreenEdges(PyObject* self, PyObject* args)
{
    PyObject* inTri, * pTri;
    if (!PyArg_ParseTuple(args, "O", &inTri))
        return NULL;
    Triangle in;
    std::vector<Triangle> out;
    in = PyTriToCTri(inTri);
    out = TriClipAgainstScreenEdges(in);
    int nd = out.size();
    
    if (nd > 0)
    {
        PyObject* ret = PyList_New(nd);
        for (int t = 0; t < nd; t++)
        {
            pTri = PyList_New(6);
            PyList_SetItem(pTri, 0, VectorUVToPyList(out[t].p1));
            PyList_SetItem(pTri, 1, VectorUVToPyList(out[t].p2));
            PyList_SetItem(pTri, 2, VectorUVToPyList(out[t].p3));
            PyList_SetItem(pTri, 3, Vector3ToPyList(out[t].normal));
            PyList_SetItem(pTri, 4, Vector3ToPyList(out[t].wpos));
            PyList_SetItem(pTri, 5, PyFloat_FromDouble(out[t].shade));
            PyList_SetItem(ret, t, pTri);
        }
        return ret;
    }
    return PyList_New(0);
}

static PyObject* CTriClipAgainstZ(PyObject* self, PyObject* args)
{
    PyObject* inTri, * pTri;
    if (!PyArg_ParseTuple(args, "O", &inTri))
        return NULL;
    Triangle in;
    std::vector<Triangle> out;
    in = PyTriToCTri(inTri);

    out = TriClipAgainstPlane(in, { 0.0, 0.0, 0.0 }, { 0.0, 0.0, 1.0 });
    int nd = out.size();
    if (nd > 0)
    {
        PyObject* ret = PyList_New(nd);

        for (int t = 0; t < nd; t++)
        {
            pTri = PyList_New(6);
            PyList_SetItem(pTri, 0, VectorUVToPyList(out[t].p1));
            PyList_SetItem(pTri, 1, VectorUVToPyList(out[t].p2));
            PyList_SetItem(pTri, 2, VectorUVToPyList(out[t].p3));
            PyList_SetItem(pTri, 3, Vector3ToPyList(out[t].normal));
            PyList_SetItem(pTri, 4, Vector3ToPyList(out[t].wpos));
            PyList_SetItem(pTri, 5, PyFloat_FromDouble(out[t].shade));
            PyList_SetItem(ret, t, pTri);
        }
        return ret;
    }
    return PyList_New(0);
}

static void CSetInternalCamera(PyObject* self, PyObject* args)
{
    PyObject* inCam;
    if (!PyArg_ParseTuple(args, "O", &inCam))
        return;
    CamPos = PyVectorToVector3(PyList_GetItem(inCam, 0));
    scrW = PyFloat_AsDouble(PyList_GetItem(inCam, 3));
    scrH = PyFloat_AsDouble(PyList_GetItem(inCam, 2));
    CamTrg = PyVectorToVector3(PyList_GetItem(inCam, 6));
    matV = MakeLookMat(CamPos, CamTrg, { 0.f, 1.f, 0.f });
}

static PyObject* CRasterIndex(PyObject* self, PyObject* args)
{
    int pyInd;
    PyObject* ppos, * prot;
    Vector3 pos, rot;

    if (!PyArg_ParseTuple(args, "iOO", &pyInd, &ppos, &prot))
        return NULL;

    pos = PyVectorToVector3(ppos);
    rot = PyVectorToVector3(prot);
    Triangle transformed, translated;
    std::vector<Triangle> rastered;
    Matrix mW;

    mW = MakeRotMatX(rot.x);
    mW = MatrixMatrixMul(mW, MakeRotMatY(rot.y));
    mW = MatrixMatrixMul(mW, MakeRotMatZ(rot.z));
    
    Vector3 nrmTrg = VectorNormalize(VectorSub(CamTrg, CamPos));

    // Rastering
    for (const Thing thing : things)
    {
        for (const Mesh mesh : thing.meshes)
        {
            for (const Triangle tri : mesh.tris)
            {
                transformed = TransformTriangle(tri, mW);
                transformed.normal = GetNormal(transformed);
                if (VectorDoP(transformed.normal, nrmTrg) > -0.4)
                {
                    translated = TriangleAdd(transformed, pos);
                    translated.wpos = TriangleAverage(translated);
                    //viewed = TriMatrixMul(tri, matV);
                    rastered.push_back(translated);
                }
            }
        }
    }

    // Converting C triangle to Python list
    PyObject* newList = PyList_New(rastered.size());
    PyObject* triList;
    for (int b = 0; b < rastered.size(); b++)
    {
        // Converting C vector to Python list
        triList = PyList_New(6);
        PyList_SetItem(triList, 0, VectorUVToPyList(rastered[b].p1));
        PyList_SetItem(triList, 1, VectorUVToPyList(rastered[b].p2));
        PyList_SetItem(triList, 2, VectorUVToPyList(rastered[b].p3));
        PyList_SetItem(triList, 3, Vector3ToPyList(rastered[b].normal));
        PyList_SetItem(triList, 4, Vector3ToPyList(rastered[b].wpos));
        PyList_SetItem(triList, 5, PyFloat_FromDouble(rastered[b].shade));

        PyList_SetItem(newList, b, triList);
    }
    return newList;
}

static PyObject* AddLight(PyObject* self, PyObject* args)
{
    PyObject* light;
    if (PyArg_ParseTuple(args, "O", &light))
    {
        Light_Point nL;
        nL.pos = PyVectorToVector3(PyList_GetItem(light, 0));
        nL.strength = PyFloat_AsDouble(PyList_GetItem(light, 1));
        nL.radius = PyFloat_AsDouble(PyList_GetItem(light, 2));
        nL.intId = (int)lights.size();
        lights.push_back(nL);
        return PyLong_FromLong(nL.intId);
    }
    else
        return NULL;
}

static PyObject* CheapFlatLighting(PyObject* self, PyObject* args)
{
    float *px, *py, *pz, *nx, *ny, *nz;
    if (!PyArg_ParseTuple(args, "ffffff", &px, &py, &pz, &nx, &ny, &nz))
        return NULL;

    if (lights.size() != 0)
    {
        float shading = 0.f;
        float intensity = 0.f;
        Vector3 pos;
        Vector3 nrm;
        pos = { *px, *py, *pz };
        nrm = VectorMul({ *nx, *ny, *nz }, { -1.0, 1.0, 1.0 });
        for (const auto l : lights)
        {
            float dist = DistanceBetweenVectors(pos, l.pos);
            if (dist <= l.radius)
            {
                Vector3 lightDir = DirectionBetweenVectors(l.pos, pos);
                
                float dis = dist / l.radius;
                intensity = dis * dis;
                shading += VectorDoP(lightDir, nrm) * (1 - intensity) * l.strength;
                shading = min(shading, 1);
                shading = max(shading, 0);
            }
        }
        return PyFloat_FromDouble(shading);
    }
    return PyFloat_FromDouble(0.0);
}

static PyObject* CAddThing(PyObject* self, PyObject* args)
{
    PyObject* pyMeshes;
    if (!PyArg_ParseTuple(args, "O", &pyMeshes))
    {
        return NULL;
    }
    PyObject* oM, *oTr, *trList;
    Thing nT;
    int xS = PyList_GET_SIZE(pyMeshes);
    Mesh nM;
    for (int x = 0; x < xS; x++)
    {
        oM = PyList_GetItem(pyMeshes, x);
        nM.tris = {};
        trList = PyList_GetItem(oM, 0);

        Py_ssize_t yS = PyList_GET_SIZE(trList);
        for (Py_ssize_t y = 0; y < yS; y++)
        {
            oTr = PyTuple_GetItem(trList, y);
            nM.tris.push_back({ PyVectorToVectorUV(PyList_GetItem(oTr, 0)), PyVectorToVectorUV(PyList_GetItem(oTr, 1)), PyVectorToVectorUV(PyList_GetItem(oTr, 2)), PyVectorToVector3(PyList_GetItem(oTr, 3)), PyVectorToVector3(PyList_GetItem(oTr, 4)), PyFloat_AsDouble(PyList_GetItem(oTr, 5)) });
        }
        nT.meshes.push_back(nM);
    }
    Py_ssize_t rt = things.size();
    things.push_back(nT);
    return PyLong_FromSsize_t(rt);
}

static PyObject* CTriToPixels(PyObject* self, PyObject* args)
{
    PyObject* tri;
    if (!PyArg_ParseTuple(args, "O", &tri))
    {
        return NULL;
    }
    PyObject* pixels = PyList_New(0);
    PyObject* newPxl;
    Triangle in = PyTriToCTri(tri);
    std::vector<VectorUV> Points = { in.p1, in.p2, in.p3, in.p3 };
    // Sorting by X
    if (Points[1].x < Points[0].x)
    {
        Points[3] = Points[0];
        Points[0] = Points[1];
        Points[1] = Points[3];
    }
    if (Points[2].x < Points[1].x)
    {
        Points[3] = Points[1];
        Points[1] = Points[2];
        Points[2] = Points[3];
    }
    float diffX2 = Points[2].x - Points[0].x;
    if (diffX2 != 0)
    {
        float slope2 = (Points[2].y - Points[0].y) / diffX2;
        float diffX1 = Points[1].x - Points[0].x;
        Vector2 uv1 = { Points[0].u, Points[0].v };
        Vector2 uv2 = { Points[1].u, Points[1].v };
        Vector2 uv3 = { Points[2].u, Points[2].v };
        // UV deltas
        float uvD1 = uv2.x - uv1.x;
        float uvD2 = uv2.y - uv1.y;
        float uvD3 = uv3.x - uv1.x;
        float uvD4 = uv3.y - uv1.y;
        if (diffX1 != 0.f)
        {
            float diffY1 = Points[1].y - Points[0].y;
            float slope1 = diffY1 / diffX1;
            for (int x = 0; x < (int)diffX1 + 1; x++)
            {
                // Get the Y of the two points to interpolate.
                int range1 = slope1 * x + Points[0].y;
                int range2 = slope2 * x + Points[0].y;
                int range3 = range2 - range1;
                // Normalize from both line's perspectives.
                float nX1 = (x / diffX1);
                float nX2 = (x / diffX2);
                // Calculating UV of these new points
                float UVndX = nX2 * uvD3 + uv1.x;
                float UVndY = nX2 * uvD4 + uv1.y;
                float UVstX = nX1 * uvD1 + uv1.x;
                float UVstY = nX1 * uvD2 + uv1.y;
                // And the delta between the UVs
                float uvDy = UVndY - UVstY;
                float uvDx = UVndX - UVstX;
                int sgn = (range3 > 0) ? 1 : -1;
                for (int y = 0; y < range3; y += sgn)
                {
                    float nY = y / range3;
                    // And finally we can get the UV of the current pixel.
                    float uvY = nY * uvDy + UVstY;
                    float uvX = nY * uvDx + UVstX;
                    newPxl = PyList_New(4);
                    PyList_SetItem(newPxl, 0, PyLong_FromLong(x + (int)Points[0].x));
                    PyList_SetItem(newPxl, 1, PyLong_FromLong(y + (int)Points[0].y));
                    PyList_SetItem(newPxl, 2, PyLong_FromLong(uvX));
                    PyList_SetItem(newPxl, 3, PyLong_FromLong(uvY));
                    PyList_Append(pixels, newPxl);
                }
            }
            return pixels;
        }
    }

}

static PyMethodDef z3dpyfast_methods[] = {
    { "CAddThing", (PyCFunction)CAddThing, METH_VARARGS, nullptr },
    { "CRaster", (PyCFunction)CRasterIndex, METH_VARARGS, nullptr },
    { "CAddLight", (PyCFunction)AddLight, METH_VARARGS, nullptr },
    { "CFlatLighting", (PyCFunction)CheapFlatLighting, METH_VARARGS, nullptr },
    { "CTriClipAgainstScreenEdges", (PyCFunction)CTriClipAgainstScreenEdges, METH_VARARGS, nullptr },
    { "CTriClipAgainstZ", (PyCFunction)CTriClipAgainstZ, METH_VARARGS, nullptr },
    { "CSetInternalCamera", (PyCFunction)CSetInternalCamera, METH_VARARGS, nullptr },
    { "CTriToPixels", (PyCFunction)CTriToPixels, METH_VARARGS, nullptr },
    //{ "Template", (PyCFunction)TemplateMatrix, METH_VARARGS, nullptr },
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