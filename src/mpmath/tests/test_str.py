from mpmath import nstr, matrix, inf


def test_nstr():
    m = matrix(
        [
            [0.75, 0.190940654, -0.0299195971],
            [0.190940654, 0.65625, 0.205663228],
            [-0.0299195971, 0.205663228, 0.64453125e-20],
        ]
    )
    assert (
        nstr(m, 4, min_fixed=-inf)
        == """[    0.75  0.1909                    -0.02992]
[  0.1909  0.6563                      0.2057]
[-0.02992  0.2057  0.000000000000000000006445]"""
    )
    assert (
        nstr(m, 4)
        == """[    0.75  0.1909   -0.02992]
[  0.1909  0.6563     0.2057]
[-0.02992  0.2057  6.445e-21]"""
    )
