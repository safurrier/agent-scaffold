// Package app provides the core application logic.
package app

// Greeter demonstrates the project structure.
type Greeter struct {
	Name string
}

// Greet returns a greeting message.
func (g *Greeter) Greet() string {
	return "Hello, " + g.Name + "!"
}
