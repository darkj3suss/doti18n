.PHONY: lint format check clean publish publish-test


clean:
	@python -c "import shutil, glob; [shutil.rmtree(d) for d in ('build', 'dist') if shutil.os.path.exists(d)]; [shutil.rmtree(d) for d in glob.glob('*.egg-info')];"


publish-test: clean
	python -m build
	twine check dist/*
	twine upload --repository testpypi dist/*


publish: clean
	python -m build
	twine check dist/*
	twine upload dist/*


lint:
	ruff check .

format:
	ruff check . --fix
	black .

check:
	ruff check .
	black --check .
	mypy .
