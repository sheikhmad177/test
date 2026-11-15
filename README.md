# Prototype 1

`index.html` is the standalone Control / Prototype A source file. It includes HTML, CSS, JavaScript, and embedded product images. Open it directly in a browser; no installation or server is required.

The original five-screen simulated checkout, editable delivery details, gift-box toggle, participant mode, and in-memory study-event log with CSV export are preserved. No actual payment is processed. Events disappear on reload unless exported.

Regenerate and verify the same file with:

```sh
python3 split_prototypes.py && node test_prototypes.cjs
```

The original input, downloaded combined source, and image assets remain as supporting extraction inputs. Only Prototype 1 is generated and delivered.
