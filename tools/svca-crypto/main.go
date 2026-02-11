package main

import (
	"crypto/ed25519"
	"crypto/rand"
	"crypto/x509"
	"encoding/base64"
	"encoding/pem"
	"errors"
	"flag"
	"fmt"
	"os"
)

func main() {
	if len(os.Args) < 2 {
		fatal("usage: svca-crypto <keygen|sign|verify>")
	}

	switch os.Args[1] {
	case "keygen":
		keygenCmd(os.Args[2:])
	case "sign":
		signCmd(os.Args[2:])
	case "verify":
		verifyCmd(os.Args[2:])
	default:
		fatal("unknown command")
	}
}

func keygenCmd(args []string) {
	fs := flag.NewFlagSet("keygen", flag.ExitOnError)
	pubPath := fs.String("pub", "capsule/pubkey.pem", "public key path")
	secPath := fs.String("sec", "capsule/secret.key", "private key path")
	_ = fs.Parse(args)

	pub, priv, err := ed25519.GenerateKey(rand.Reader)
	if err != nil {
		fatalErr(err)
	}

	pubDer, err := x509.MarshalPKIXPublicKey(pub)
	if err != nil {
		fatalErr(err)
	}
	privDer, err := x509.MarshalPKCS8PrivateKey(priv)
	if err != nil {
		fatalErr(err)
	}

	if err := writePEM(*pubPath, "PUBLIC KEY", pubDer, 0o644); err != nil {
		fatalErr(err)
	}
	if err := writePEM(*secPath, "PRIVATE KEY", privDer, 0o600); err != nil {
		fatalErr(err)
	}

	fmt.Println("keys generated")
}

func signCmd(args []string) {
	fs := flag.NewFlagSet("sign", flag.ExitOnError)
	secPath := fs.String("sec", "capsule/secret.key", "private key path")
	inPath := fs.String("in", "build/manifest.sha256", "input file")
	outPath := fs.String("out", "build/signature.bin", "signature file")
	_ = fs.Parse(args)

	priv, err := readPrivateKey(*secPath)
	if err != nil {
		fatalErr(err)
	}
	msg, err := os.ReadFile(*inPath)
	if err != nil {
		fatalErr(err)
	}
	sig := ed25519.Sign(priv, msg)
	if err := os.WriteFile(*outPath, []byte(base64.StdEncoding.EncodeToString(sig)), 0o644); err != nil {
		fatalErr(err)
	}

	fmt.Println("signature created")
}

func verifyCmd(args []string) {
	fs := flag.NewFlagSet("verify", flag.ExitOnError)
	pubPath := fs.String("pub", "capsule/pubkey.pem", "public key path")
	inPath := fs.String("in", "build/manifest.sha256", "input file")
	sigPath := fs.String("sig", "build/signature.bin", "signature file")
	_ = fs.Parse(args)

	pub, err := readPublicKey(*pubPath)
	if err != nil {
		fatalErr(err)
	}
	msg, err := os.ReadFile(*inPath)
	if err != nil {
		fatalErr(err)
	}
	sigB64, err := os.ReadFile(*sigPath)
	if err != nil {
		fatalErr(err)
	}
	sig, err := base64.StdEncoding.DecodeString(string(sigB64))
	if err != nil {
		fatalErr(err)
	}
	if !ed25519.Verify(pub, msg, sig) {
		fatal("signature invalid")
	}
	fmt.Println("signature valid")
}

func writePEM(path, kind string, der []byte, perm os.FileMode) error {
	block := &pem.Block{Type: kind, Bytes: der}
	f, err := os.OpenFile(path, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, perm)
	if err != nil {
		return err
	}
	defer f.Close()
	return pem.Encode(f, block)
}

func readPublicKey(path string) (ed25519.PublicKey, error) {
	b, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	blk, _ := pem.Decode(b)
	if blk == nil {
		return nil, errors.New("invalid public key pem")
	}
	k, err := x509.ParsePKIXPublicKey(blk.Bytes)
	if err != nil {
		return nil, err
	}
	pub, ok := k.(ed25519.PublicKey)
	if !ok {
		return nil, errors.New("public key is not ed25519")
	}
	return pub, nil
}

func readPrivateKey(path string) (ed25519.PrivateKey, error) {
	b, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	blk, _ := pem.Decode(b)
	if blk == nil {
		return nil, errors.New("invalid private key pem")
	}
	k, err := x509.ParsePKCS8PrivateKey(blk.Bytes)
	if err != nil {
		return nil, err
	}
	priv, ok := k.(ed25519.PrivateKey)
	if !ok {
		return nil, errors.New("private key is not ed25519")
	}
	return priv, nil
}

func fatalErr(err error) { fatal(err.Error()) }
func fatal(msg string) {
	fmt.Fprintln(os.Stderr, msg)
	os.Exit(1)
}
