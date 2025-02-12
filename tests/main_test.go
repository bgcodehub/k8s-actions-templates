package main

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestHomeHandler(t *testing.T) {
	req := httptest.NewRequest("GET", "/", nil)
	w := httptest.NewRecorder()

	homeHandler(w, req)

	resp := w.Result()

	assert.Equal(t, http.StatusOK, resp.StatusCode, "Expected status OK")
}