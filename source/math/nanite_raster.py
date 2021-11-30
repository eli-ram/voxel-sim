

"""

// Basic

for (uint y = min_pixel.y; y < max_pixel.y; y++)
{
    float CX0 = CY0;
    float CX1 = CY1;
    float CX2 = CY2;
    float ZX = ZY;

    for (uint x = min_pixel.x; x < max_pixel.x; x++)
    {
        if (min(CX0, CX1, CX2) >= 0)
        {
            WritePixel(pixel_value, x, y, ZX);
        }

        CX0 -= edge01.y;
        CX1 -= edge12.y;
        CX2 -= edge20.y;

        ZX += grad_z.x;
    }

    CY0 += edge01.x;
    CY1 += edge12.x;
    CY2 += edge20.x;

    ZY += grad_z.y;

}

"""


"""

// Optimized

float3 edge012 = { edge01.y, edge12.y, edge20.y };
bool3 open_edge = edge012 < 0;
float3 inv_edge012 = edge012 == 0 ? 1e8 : rcp( edge012 ); // 1 / x

for (uint y = min_pixel.y; y < max_pixel.y; y++)
{

    float3 cross_x = float3( CY0, CY1, CY2 ) * inv_edge012;
    float3 min_x = open_edge ? cross_x : 0;
    float3 max_x = open_edge ? max_pixel.x - min_pixel.x : cross_x;

    float x0 = ceil( max(min_x) );
    float x1 = min(max_x);
    float ZX = ZY + GradZ.x * x0;

    x0 += min_pixel.x;
    x1 += min_pixel.y;
    for (float x = x0; x <= x1; x++)
    {
        WritePixel(pixel_value, x, y, ZX);
        ZX += grad_z.x;
    }

    CY0 += edge01.x;
    CY1 += edge12.x;
    CY2 += edge20.x;

    ZY += grad_z.y;
}


"""