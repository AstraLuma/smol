"""
Anagram of direg--Dependency Injection REGistry

An async-oriented dependency injection registry.
"""
import asyncio
import inspect
import colllections.abc
import functools

__all__ = 'AsyncInit', 'inject', 'registry'


class AsyncInit(type):
    """
    Metaclass to support the __ainit__() method.

    Note that calling this class will produce an awaitable for the instance, not
    the instance directly.
    """

    async def __call__(cls, *pargs, **kwargs):
        self = super().__call__(*pargs, **kwargs)
        if hasattr('__ainit__', cls):
            await cls.__ainit__(self, *pargs, **kwargs)
        return self


def mkfuture(val):
    if inspect.isawaitable(val):
        return asyncio.ensure_future(val)
    else:
        f = asyncio.get_event_loop().create_future()
        f.set_result(val)
        return f



class _Registry(colllections.abc.MutableMapping):
    """
    Global registry of identifiers.

    Mapping of names -> Futures.
    """
    def __init__(self):
        self.factories = {}
        self._instances = {}

    def __getitem__(self, key):
        if key not in self._instances:
            self._instances[key] = mkfuture(self.factories[key]())
        return self._instances[key]

    def __setitem__(self, key, value):
        if not isinstance(asyncio.Future):
            value = mkfuture(value)
        self._instances[key] = value

    def __len__(self):
        return len(set(self.factories.keys()) + set(self._instances.keys()))

    def __iter__(self):
        yield from set(self.factories.keys()) + set(self._instances.keys())

    def __delitem__(self, key):
        """
        NOTE: Only deletes the instance, NOT the factory. For that, check
        unregister()
        """
        del self._instances[key]

    def register(self, name_or_callable, factory=None):
        """
        r.register(name, callable)
        @r.register
        @r.register(name)

        Register a factory--a type or other callable.

        If no name is given, the __name__ of the factory is used.
        """
        def _(n, f):
            self.factories[n] = f
            return f
        if factory is not None:
            return _(name_or_callable, factory)
        elif callable(name_or_callable):
            return _(name_or_callable.__name__, name_or_callable)
        else:
            return functools.partial(_, name_or_callable)

    def unregister(self, name):
        del self.factories[name]

    def wrap(self, name):
        """
        Wraps the normal factory with the decorated callable.

        Useful for additional application-specific configuration.

        NOTE: Must be called after the factory has been registered.
        """
        def _(wrapper):
            oldfactory = self.factories[name]
            @functools.wraps(wrapper)
            async def newfactory(*pargs, **kwargs):
                return wrapper(await oldfactory(*pargs, **kwargs))
            self.factories[name] = newfactory

            # XXX: This could lead to weird behavior?
            if name in self._instances:
                self._instances[name] = mkfuture(wrapper(self._instances[name]))

        return _


registry = _Registry()


class inject:
    """
    Resolve an injection.

    Note that this will retrun to a future--always await it.

    class Spam:
        egg = inject('egg')

        async def mymethod(self):
            (await self.egg).fry()
    """
    def __init__(self, name):
        if hasattr(name, '__name__'):
            name = name.__name__
        self.name = name

    def __get__(self, obj, type=None):
        try:
            return registry[self.name]
        except KeyError:
            raise AttributeError
