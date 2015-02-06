#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Source and Receiver classes of Instaseis.

:copyright:
    Lion Krischer (krischer@geophysik.uni-muenchen.de), 2014
    Martin van Driel (Martin@vanDriel.de), 2014
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lgpl.html)
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import collections
import functools
import numpy as np
import obspy
from obspy.core.util.geodetics import FlinnEngdahl
from obspy.signal.filter import lowpass
from obspy.signal.util import nextpow2
import obspy.xseed
import os
from scipy import interp
import warnings

#from . import ReceiverParseError, SourceParseError
#from . import rotations

DEFAULT_MU = 32e9


def _purge_duplicates(f):
    """
    Simple decorator removing duplicates in the returned list. Preserves the
    order and will remove duplicates occuring later in the list.
    """
    @functools.wraps(f)
    def wrapper(*args, **kwds):
        ret_val = f(*args, **kwds)
        new_list = []
        for item in ret_val:
            if item in new_list:
                continue
            new_list.append(item)
        return new_list
    return wrapper


class SourceOrReceiver(object):
    def __init__(self, latitude, longitude, depth_in_m):
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.depth_in_m = float(depth_in_m) if depth_in_m is not None else None

        if not (-90 <= self.latitude <= 90):
            raise ValueError("Invalid Latitude Value")

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def colatitude(self):
        return 90.0 - self.latitude

    @property
    def colatitude_rad(self):
        return np.deg2rad(90.0 - self.latitude)

    @property
    def longitude_rad(self):
        return np.deg2rad(self.longitude)

    @property
    def latitude_rad(self):
        return np.deg2rad(self.latitude)

    def radius_in_m(self, planet_radius=6371e3):
        if self.depth_in_m is None:
            return planet_radius
        else:
            return planet_radius - self.depth_in_m

    def x(self, planet_radius=6371e3):
        return np.cos(np.deg2rad(self.latitude)) * \
            np.cos(np.deg2rad(self.longitude)) * \
            self.radius_in_m(planet_radius=planet_radius)

    def y(self, planet_radius=6371e3):
        return np.cos(np.deg2rad(self.latitude)) * \
            np.sin(np.deg2rad(self.longitude)) * \
            self.radius_in_m(planet_radius=planet_radius)

    def z(self, planet_radius=6371e3):
        return np.sin(np.deg2rad(self.latitude)) * \
            self.radius_in_m(planet_radius=planet_radius)


class Source(SourceOrReceiver):
    """
    A class to handle a seimic moment tensor source including a source time
    function.
    """
    def __init__(self, latitude, longitude, depth_in_m=None, m_rr=0.0,
                 m_tt=0.0, m_pp=0.0, m_rt=0.0, m_rp=0.0, m_tp=0.0,
                 time_shift=None, sliprate=None, dt=None,
                 origin_time=obspy.UTCDateTime(0)):
        """
        :param latitude: latitude of the source in degree
        :param longitude: longitude of the source in degree
        :param depth_in_m: source depth in m
        :param m_rr: moment tensor components in r, theta, phi in Nm
        :param m_tt: moment tensor components in r, theta, phi in Nm
        :param m_pp: moment tensor components in r, theta, phi in Nm
        :param m_rt: moment tensor components in r, theta, phi in Nm
        :param m_rp: moment tensor components in r, theta, phi in Nm
        :param m_tp: moment tensor components in r, theta, phi in Nm
        :param time_shift: correction of the origin time in seconds. only
            useful in the context of finite sources
        :param sliprate: normalized source time function (sliprate)
        :param dt: sampling of the source time function
        :param origin_time: The origin time of the source. This will be the
            time of the first sample in the final seismogram. Be careful to
            adjust it for any time shift or STF (de)convolution effects.


        >>> import instaseis
        >>> source = instaseis.Source(
        ...     latitude=89.91, longitude=0.0, depth_in_m=12000,
        ...     m_rr = 4.71e+17, m_tt = 3.81e+15, m_pp =-4.74e+17,
        ...     m_rt = 3.99e+16, m_rp =-8.05e+16, m_tp =-1.23e+17)
        >>> print(source)
        Instaseis Source:
            Longitude        :    0.0 deg
            Latitude         :   89.9 deg
            Depth            : 1.2e+01 km
            Moment Magnitude :   5.80
            Scalar Moment    :   4.96e+17 Nm
            Mrr              :   4.71e+17 Nm
            Mtt              :   3.81e+15 Nm
            Mpp              :  -4.74e+17 Nm
            Mrt              :   3.99e+16 Nm
            Mrp              :  -8.05e+16 Nm
            Mtp              :  -1.23e+17 Nm
        """
        super(Source, self).__init__(latitude, longitude, depth_in_m)
        self.m_rr = m_rr
        self.m_tt = m_tt
        self.m_pp = m_pp
        self.m_rt = m_rt
        self.m_rp = m_rp
        self.m_tp = m_tp
        self.origin_time = origin_time
        self.time_shift = time_shift
        self.sliprate = np.array(sliprate) if sliprate is not None else None
        self.dt = dt

    @staticmethod
    def parse(filename_or_obj):
        """
        Attempts to parse anything to a Source object. Can currently read
        anything ObsPy can read, ObsPy event related objects,
        and CMTSOLUTION files.

        For anything ObsPy related, it must contain a full moment tensor,
        otherwise it will raise an error.

        :param filename_or_obj: The object or filename to parse.


        The following example will read a local QuakeML file and return a
        :class:`~instaseis.source.Source` object.

        >>> import instaseis
        >>> source = instaseis.Source.parse("quake.xml")
        >>> print(source)
        Instaseis Source:
            Longitude        :   -3.5 deg
            Latitude         :   37.0 deg
            Depth            : 6.1e+02 km
            Moment Magnitude :   6.41
            Scalar Moment    :   4.16e+18 Nm
            Mrr              :  -2.16e+18 Nm
            Mtt              :   5.36e+17 Nm
            Mpp              :   1.62e+18 Nm
            Mrt              :   1.30e+16 Nm
            Mrp              :   3.23e+18 Nm
            Mtp              :   1.75e+18 Nm
        """
        if isinstance(filename_or_obj, (str, bytes)):
            # Anything ObsPy can read.
            try:
                src = obspy.readEvents(filename_or_obj)
            except:
                pass
            else:
                return Source.parse(src)
            # CMT solution file.
            try:
                return Source.from_CMTSOLUTION_file(filename_or_obj)
            except:
                pass
            raise SourceParseError("Could not parse the given source.")
        elif isinstance(filename_or_obj, obspy.Catalog):
            if len(filename_or_obj) == 0:
                raise SourceParseError("Event catalog contains zero events.")
            elif len(filename_or_obj) > 1:
                raise SourceParseError(
                    "Event catalog contains %i events. Only one is allowed. "
                    "Please parse seperately." % len(filename_or_obj))
            return Source.parse(filename_or_obj[0])
        elif isinstance(filename_or_obj, obspy.core.event.Event):
            ev = filename_or_obj
            if not ev.origins:
                raise SourceParseError("Event must contain an origin.")
            if not ev.focal_mechanisms:
                raise SourceParseError("Event must contain a focal mechanism.")
            org = ev.preferred_origin() or ev.origins[0]
            fm = ev.preferred_focal_mechanism() or ev.focal_mechansisms[0]
            if not fm.moment_tensor:
                raise SourceParseError("Event must contain a moment tensor.")
            t = fm.moment_tensor.tensor
            return Source(
                latitude=org.latitude,
                longitude=org.longitude,
                depth_in_m=org.depth,
                origin_time=org.time,
                m_rr=t.m_rr,
                m_tt=t.m_tt,
                m_pp=t.m_pp,
                m_rt=t.m_rt,
                m_rp=t.m_rp,
                m_tp=t.m_tp)
        else:
            raise NotImplementedError

    @classmethod
    def from_CMTSOLUTION_file(self, filename):
        """
        Initialize a source object from a CMTSOLUTION file.

        :param filename: path to the CMTSOLUTION file

        >>> import instaseis
        >>> source = instaseis.Source.from_CMTSOLUTION_file('file.cmt')
        >>> print(source)
        Instaseis Source:
            Longitude        : -177.0 deg
            Latitude         :  -29.2 deg
            Depth            : 4.8e+01 km
            Moment Magnitude :   7.32
            Scalar Moment    :   9.63e+19 Nm
            Mrr              :   7.68e+19 Nm
            Mtt              :   9.00e+17 Nm
            Mpp              :  -7.77e+19 Nm
            Mrt              :   1.39e+19 Nm
            Mrp              :   4.52e+19 Nm
            Mtp              :  -3.26e+19 Nm
        """
        with open(filename, "rt") as f:
            line = f.readline()
            origin_time = line[4:].strip().split()[:6]
            values = list(map(int, origin_time[:-1])) + \
                [float(origin_time[-1])]
            try:
                origin_time = obspy.UTCDateTime(*values)
            except (TypeError, ValueError):
                warnings.warn("Could not determine origin time from line: %s"
                              % line)
                origin_time = obspy.UTCDateTime(0)
            f.readline()
            time_shift = float(f.readline().strip().split()[-1])
            f.readline()
            latitude = float(f.readline().strip().split()[-1])
            longitude = float(f.readline().strip().split()[-1])
            depth_in_m = float(f.readline().strip().split()[-1]) * 1e3

            m_rr = float(f.readline().strip().split()[-1]) / 1e7
            m_tt = float(f.readline().strip().split()[-1]) / 1e7
            m_pp = float(f.readline().strip().split()[-1]) / 1e7
            m_rt = float(f.readline().strip().split()[-1]) / 1e7
            m_rp = float(f.readline().strip().split()[-1]) / 1e7
            m_tp = float(f.readline().strip().split()[-1]) / 1e7

        return self(latitude, longitude, depth_in_m, m_rr, m_tt, m_pp, m_rt,
                    m_rp, m_tp, time_shift, origin_time=origin_time)

    @classmethod
    def from_strike_dip_rake(self, latitude, longitude, depth_in_m, strike,
                             dip, rake, M0, time_shift=None, sliprate=None,
                             dt=None, origin_time=obspy.UTCDateTime(0)):
        """
        Initialize a source object from a shear source parameterized by strike,
        dip and rake.

        :param latitude: latitude of the source in degree
        :param longitude: longitude of the source in degree
        :param depth_in_m: source depth in m
        :param strike: strike of the fault in degree
        :param dip: dip of the fault in degree
        :param rake: rake of the fault in degree
        :param M0: scalar moment
        :param time_shift: correction of the origin time in seconds. only
            useful in the context of finite sources
        :param sliprate: normalized source time function (sliprate)
        :param dt: sampling of the source time function
        :param origin_time: The origin time of the source. This will be the
            time of the first sample in the final seismogram. Be careful to
            adjust it for any time shift or STF (de)convolution effects.

        >>> import instaseis
        >>> source = instaseis.Source.from_strike_dip_rake(
        ...     latitude=10.0, longitude=12.0, depth_in_m=1000, strike=79,
        ...     dip=10, rake=20, M0=1E17)
        >>> print(source)
        Instaseis Source:
            Longitude        :   12.0 deg
            Latitude         :   10.0 deg
            Depth            : 1.0e+00 km
            Moment Magnitude :   5.33
            Scalar Moment    :   1.00e+17 Nm
            Mrr              :   1.17e+16 Nm
            Mtt              :  -1.74e+16 Nm
            Mpp              :   5.69e+15 Nm
            Mrt              :  -4.92e+16 Nm
            Mrp              :   8.47e+16 Nm
            Mtp              :   1.29e+16 Nm
        """
        # formulas in Udias (17.24) are in geographic system North, East,
        # Down, which # transforms to the geocentric as:
        # Mtt =  Mxx, Mpp = Myy, Mrr =  Mzz
        # Mrp = -Myz, Mrt = Mxz, Mtp = -Mxy
        # voigt in tpr: Mtt Mpp Mrr Mrp Mrt Mtp
        phi = np.deg2rad(strike)
        delta = np.deg2rad(dip)
        lambd = np.deg2rad(rake)

        m_tt = (- np.sin(delta) * np.cos(lambd) * np.sin(2. * phi)
                - np.sin(2. * delta) * np.sin(phi)**2. * np.sin(lambd)) * M0

        m_pp = (np.sin(delta) * np.cos(lambd) * np.sin(2. * phi)
                - np.sin(2. * delta) * np.cos(phi)**2. * np.sin(lambd)) * M0

        m_rr = (np.sin(2. * delta) * np.sin(lambd)) * M0

        m_rp = (- np.cos(phi) * np.sin(lambd) * np.cos(2. * delta)
                + np.cos(delta) * np.cos(lambd) * np.sin(phi)) * M0

        m_rt = (- np.sin(lambd) * np.sin(phi) * np.cos(2. * delta)
                - np.cos(delta) * np.cos(lambd) * np.cos(phi)) * M0

        m_tp = (- np.sin(delta) * np.cos(lambd) * np.cos(2. * phi)
                - np.sin(2. * delta) * np.sin(2. * phi) * np.sin(lambd) / 2.) \
            * M0

        source = self(latitude, longitude, depth_in_m, m_rr, m_tt, m_pp, m_rt,
                      m_rp, m_tp, time_shift, sliprate, dt,
                      origin_time=origin_time)

        # storing strike, dip and rake for plotting purposes
        source.phi = phi
        source.delta = delta
        source.lambd = lambd

        return source

    def write_CMTSOLUTION_file(self, filename):
        """
        Initialize a source object from a CMTSOLUTION file.

        :param filename: path to the CMTSOLUTION file
        """
        with open(filename, "w") as f:
            # Reconstruct the first line as well as possible. All
            # hypocentral information is missing.
            f.write('    %4i %2i %2i %2i %2i %5.2f %8.4f %9.4f %5.1f %.1f %.1f'
                    ' %s\n' % (
                        self.origin_time.year,
                        self.origin_time.month,
                        self.origin_time.day,
                        self.origin_time.hour,
                        self.origin_time.minute,
                        self.origin_time.second +
                        self.origin_time.microsecond / 1E6,
                        self.latitude,
                        self.longitude,
                        self.depth_in_m / 1e3,
                        # Just write the moment magnitude twice...we don't
                        # have any other.
                        self.moment_magnitude,
                        self.moment_magnitude,
                        FlinnEngdahl().get_region(self.longitude,
                                                  self.latitude)))
            f.write('event name:  nn\n')
            f.write('time shift:     %5.2f\n' % (self.time_shift,))
            f.write('half duration:  0.0\n')
            f.write('latitude:       %7.4f\n' % (self.latitude,))
            f.write('longitude:      %7.4f\n' % (self.longitude,))
            f.write('depth:          %7.4f\n' % (self.depth_in_m / 1e3,))

            f.write('Mrr:            %7.4f\n' % (self.m_rr * 1e7,))
            f.write('Mtt:            %7.4f\n' % (self.m_tt * 1e7,))
            f.write('Mpp:            %7.4f\n' % (self.m_pp * 1e7,))
            f.write('Mrt:            %7.4f\n' % (self.m_rt * 1e7,))
            f.write('Mrp:            %7.4f\n' % (self.m_rp * 1e7,))
            f.write('Mtp:            %7.4f\n' % (self.m_tp * 1e7,))

    @property
    def M0(self):
        """
        Scalar Moment M0 in Nm
        """
        return (self.m_rr ** 2 + self.m_tt ** 2 + self.m_pp ** 2
                + 2 * self.m_rt ** 2 + 2 * self.m_rp ** 2
                + 2 * self.m_tp ** 2) ** 0.5 * 0.5 ** 0.5

    @property
    def moment_magnitude(self):
        """
        Moment magnitude M_w
        """
        return 2.0 / 3.0 * np.log10(self.M0) - 6.0

    @property
    def tensor(self):
        """
        List of moment tensor components in r, theta, phi coordinates:
        [m_rr, m_tt, m_pp, m_rt, m_rp, m_tp]
        """
        return np.array([self.m_rr, self.m_tt, self.m_pp, self.m_rt, self.m_rp,
                         self.m_tp])

    @property
    def tensor_voigt(self):
        """
        List of moment tensor components in theta, phi, r coordinates in Voigt
        notation:
        [m_tt, m_pp, m_rr, m_rp, m_rt, m_tp]
        """
        return np.array([self.m_tt, self.m_pp, self.m_rr, self.m_rp, self.m_rt,
                         self.m_tp])

    def set_sliprate(self, sliprate, dt, time_shift=None, normalize=True):
        """
        Add a source time function (sliprate) to a initialized source object.

        :param sliprate: (normalized) sliprate
        :param dt: sampling of the sliprate
        :param normalize: if sliprate is not normalized, set this to true to
            normalize it using trapezoidal rule style integration
        """
        self.sliprate = np.array(sliprate)
        if normalize:
            self.sliprate /= np.trapz(sliprate, dx=dt)
        self.dt = dt
        self.time_shift = time_shift

    def resample_sliprate(self, dt, nsamp):
        """
        For convolution, the sliprate is needed at the sampling of the fields
        in the database. This function resamples the sliprate using linear
        interpolation.

        :param dt: desired sampling
        :param nsamp: desired number of samples
        """
        t_new = np.linspace(0, nsamp * dt, nsamp, endpoint=False)
        t_old = np.linspace(0, self.dt * len(self.sliprate),
                            len(self.sliprate), endpoint=False)

        self.sliprate = interp(t_new, t_old, self.sliprate)
        self.dt = dt

    def set_sliprate_dirac(self, dt, nsamp):
        """
        :param dt: desired sampling
        :param nsamp: desired number of samples
        """
        self.sliprate = np.zeros(nsamp)
        self.sliprate[0] = 1.0 / dt
        self.dt = dt

    def set_sliprate_lp(self, dt, nsamp, freq, corners=4, zerophase=False):
        """
        :param dt: desired sampling
        :param nsamp: desired number of samples
        """
        self.sliprate = np.zeros(nsamp)
        self.sliprate[0] = 1.0 / dt
        self.sliprate = lowpass(self.sliprate, freq, 1./dt, corners, zerophase)
        self.dt = dt

    def normalize_sliprate(self):
        """
        normalize the sliprate using trapezoidal rule
        """
        self.sliprate /= np.trapz(self.sliprate, dx=self.dt)

    def lp_sliprate(self, freq, corners=4, zerophase=False):
        self.sliprate = lowpass(self.sliprate, freq, 1./self.dt, corners,
                                zerophase)

    def __str__(self):
        return_str = 'Instaseis Source:\n'
        return_str += '\tLongitude        : %6.1f deg\n' % (self.longitude,)
        return_str += '\tLatitude         : %6.1f deg\n' % (self.latitude,)
        return_str += '\tDepth            : %6.1e km\n' \
                      % (self.depth_in_m / 1e3,)
        return_str += '\tMoment Magnitude :   %4.2f\n' \
                      % (self.moment_magnitude,)
        return_str += '\tScalar Moment    : %10.2e Nm\n' % (self.M0,)
        return_str += '\tMrr              : %10.2e Nm\n' % (self.m_rr,)
        return_str += '\tMtt              : %10.2e Nm\n' % (self.m_tt,)
        return_str += '\tMpp              : %10.2e Nm\n' % (self.m_pp,)
        return_str += '\tMrt              : %10.2e Nm\n' % (self.m_rt,)
        return_str += '\tMrp              : %10.2e Nm\n' % (self.m_rp,)
        return_str += '\tMtp              : %10.2e Nm\n' % (self.m_tp,)

        return return_str


class ForceSource(SourceOrReceiver):
    """
    A class to handle a seimic force source.

    :param latitude: latitude of the source in degree
    :param longitude: longitude of the source in degree
    :param depth_in_m: source depth in m
    :param f_r: force components in r, theta, phi in N
    :param f_t: force components in r, theta, phi in N
    :param f_p: force components in r, theta, phi in N
    :param origin_time: The origin time of the source. This will be the
        time of the first sample in the final seismogram. Be careful to
        adjust it for any time shift or STF (de)convolution effects.


    >>> import instaseis
    >>> source = instaseis.ForceSource(latitude=12.34, longitude=12.34,
    ...                                f_r=1E10)
    >>> print(source)
    Instaseis Force Source:
        longitude :   12.3 deg
        latitude  :   12.3 deg
        Fr        :   1.00e+10 N
        Ft        :   0.00e+00 N
        Fp        :   0.00e+00 N
    """
    def __init__(self, latitude, longitude, depth_in_m=None, f_r=0., f_t=0.,
                 f_p=0., origin_time=obspy.UTCDateTime(0)):
        super(ForceSource, self).__init__(latitude, longitude, depth_in_m)
        self.f_r = f_r
        self.f_t = f_t
        self.f_p = f_p
        self.origin_time = origin_time

    @property
    def force_tpr(self):
        """
        List of force components in theta, phi, r coordinates:
        [f_t, f_p, f_r]
        """
        return np.array([self.f_t, self.f_p, self.f_r])

    @property
    def force_rtp(self):
        """
        List of force components in r, theta, phi, coordinates:
        [f_r, f_t, f_p]
        """
        return np.array([self.f_t, self.f_p, self.f_r])

    def __str__(self):
        return_str = 'Instaseis Force Source:\n'
        return_str += '\tlongitude : %6.1f deg\n' % (self.longitude)
        return_str += '\tlatitude  : %6.1f deg\n' % (self.latitude)
        return_str += '\tFr        : %10.2e N\n' % (self.f_r)
        return_str += '\tFt        : %10.2e N\n' % (self.f_t)
        return_str += '\tFp        : %10.2e N\n' % (self.f_p)

        return return_str

