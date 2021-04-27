# coding: utf-8
#
# Copyright 2011 Yesudeep Mangalapilly <yesudeep@gmail.com>
# Copyright 2012 Google, Inc & contributors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""
Utility collections or "bricks".

:module: watchdog.utils.bricks
:author: yesudeep@google.com (Yesudeep Mangalapilly)
:author: lalinsky@gmail.com (Lukáš Lalinský)
:author: python@rcn.com (Raymond Hettinger)
:author: contact@tiger-222.fr (Mickaël Schoentgen)

Classes
=======
.. autoclass:: OrderedSetQueue
   :members:
   :show-inheritance:
   :inherited-members:

.. autoclass:: OrderedSet

"""

import queue

import collections

class OrderedSet(collections.MutableSet):

    def __init__(self, iterable=None):
        self.end = end = [] 
        end += [None, end, end]         # sentinel node for doubly linked list
        self.map = {}                   # key --> [key, prev, next]
        if iterable is not None:
            self |= iterable

    def __len__(self):
        return len(self.map)

    def __contains__(self, key):
        return key in self.map

    def add(self, key):
        if key not in self.map:
            end = self.end
            curr = end[1]
            curr[2] = end[1] = self.map[key] = [key, curr, end]

    def discard(self, key):
        if key in self.map:        
            key, prev, next = self.map.pop(key)
            prev[2] = next
            next[1] = prev

    def __iter__(self):
        end = self.end
        curr = end[2]
        while curr is not end:
            yield curr[0]
            curr = curr[2]

    def __reversed__(self):
        end = self.end
        curr = end[1]
        while curr is not end:
            yield curr[0]
            curr = curr[1]

    def pop(self, last=False):
        if not self:
            raise KeyError('set is empty')
        key = self.end[1][0] if last else self.end[2][0]
        self.discard(key)
        return key

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def __eq__(self, other):
        if isinstance(other, OrderedSet):
            return len(self) == len(other) and list(self) == list(other)
        return set(self) == set(other)


class SkipRepeatsQueue(queue.Queue):

    """Thread-safe implementation of an special queue where a
    put of the last-item put'd will be dropped.

    The implementation leverages locking already implemented in the base class
    redefining only the primitives.

    Queued items must be immutable and hashable so that they can be used
    as dictionary keys. You must implement **only read-only properties** and
    the :meth:`Item.__hash__()`, :meth:`Item.__eq__()`, and
    :meth:`Item.__ne__()` methods for items to be hashable.

    An example implementation follows::

        class Item:
            def __init__(self, a, b):
                self._a = a
                self._b = b

            @property
            def a(self):
                return self._a

            @property
            def b(self):
                return self._b

            def _key(self):
                return (self._a, self._b)

            def __eq__(self, item):
                return self._key() == item._key()

            def __ne__(self, item):
                return self._key() != item._key()

            def __hash__(self):
                return hash(self._key())

    based on the OrderedSetQueue below
    """

    def _init(self, maxsize):
        super()._init(maxsize)
        self.queue = OrderedSet()
    def _put(self, item):
        self.queue.add(item)
    def _get(self):
        return self.queue.pop()
