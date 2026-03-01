package app

import "testing"

func TestGreet(t *testing.T) {
	t.Parallel()
	g := Greeter{Name: "World"}
	want := "Hello, World!"
	got := g.Greet()

	if got != want {
		t.Errorf("Greet() = %q, want %q", got, want)
	}
}

func TestGreetCustomName(t *testing.T) {
	t.Parallel()
	g := Greeter{Name: "Agent"}
	want := "Hello, Agent!"
	got := g.Greet()

	if got != want {
		t.Errorf("Greet() = %q, want %q", got, want)
	}
}
