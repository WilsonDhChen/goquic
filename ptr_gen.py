#!/usr/bin/env python

from string import Template
import sys


HEADER = Template('''\
package goquic

import (
	"sync"
	"math"
	"bytes"
	"fmt"
)

// Generated by `ptr_gen.py ${args}`
// Do not edit manually!


''')

TMPL = Template('''\
var ${inst}Ptr = &${cls}Ptr{pool: make(map[int64]*${cls})}

type ${cls}Ptr struct {
	sync.RWMutex
	pool  map[int64]*${cls}
	index int64
}

func (p *${cls}Ptr) Get(key int64) *${cls} {
	p.RLock()
	defer p.RUnlock()
	return p.pool[key]
}

func (p *${cls}Ptr) Set(pt *${cls}) int64 {
	p.Lock()
	defer p.Unlock()
	for {
		if _, ok := p.pool[p.index]; !ok {
			break
		}
		p.index += 1
		if p.index == math.MaxInt64 {
			p.index = 0
		}
	}
	p.pool[p.index] = pt
	p.index += 1
	return p.index - 1
}

func (p *${cls}Ptr) Del(key int64) {
	p.Lock()
	defer p.Unlock()
	delete(p.pool, key)
}

''')

FOOTER_TMPL = Template('''\
	b.WriteString(fmt.Sprintln("${cls} - ", len(${inst}Ptr.pool)))
''')


if __name__ == "__main__":
    with open("ptr.go", "w") as f:
        f.write(HEADER.substitute(args=" ".join(sys.argv[1:])))

        for t in sys.argv[1:]:
            f.write(TMPL.substitute(cls=t, inst=t[0].lower()+t[1:]))

        f.write("func DebugInfo(b *bytes.Buffer) {\n")
        for t in sys.argv[1:]:
            f.write(FOOTER_TMPL.substitute(cls=t, inst=t[0].lower()+t[1:]))
        f.write("}")
