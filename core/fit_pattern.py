from scipy.optimize import curve_fit
import numpy as np
from matplotlib import pyplot as plt


def fun_sin(x, a, b, c, d):
    return a + b * np.sin(x * c + d)


def fit_sin(x, y):
    base = np.mean(y)
    amp = (np.max(y) - np.min(y)) / 2
    freq = 2 * np.pi / 4.

    p0 = [base, amp, freq, 0]
    bounds = ([0.5 * base, amp * 0.5, 0.99 * freq,
               0], [1.5 * base, amp * 1.5, 1.01 * freq, np.pi])
    params, cov = curve_fit(fun_sin, x, y, p0=p0, bounds=bounds)
    return params


def fit(pattern):
    x = np.arange(4)
    top, bottom = fit_sin(x, pattern[0:4]), fit_sin(x, pattern[4:8])
    #print(top)
    return {
        'params': (top, bottom),
        'amp': (top[1] / top[0], bottom[1] / bottom[0]),
        'phase': (top[3], bottom[3])
    }


def test_fit_sin():
    pat = np.array([
        4.08114161, 1.99908683, 0.88988817, 2.95525983, 4.06705392, 1.99427544,
        0.90778025, 2.98661243, 0.3833843, 0.23089828, 0.05462554, 0.22189553
    ])
    x_data = np.arange(4)
    y_data = pat[0:4]
    fig = plt.figure()

    plt.scatter(x_data, y_data)
    params = fit_sin(x_data, y_data)

    x_data = np.linspace(0, 4, num=50)

    plt.plot(x_data,
             fun_sin(x_data, params[0], params[1], params[2], params[3]),
             label='Fitted function')
    plt.show()


if __name__ == '__main__':
    test_fit_sin()
