import pytest
from anaconda_assistant_conda.cli import parse_natural_language_prompt


class TestNaturalLanguageParsing:
    """Test the natural language prompt parsing functionality."""
    
    def test_create_environment_basic(self):
        """Test basic environment creation prompts."""
        prompt = "create a conda environment with python 3.8 and numpy"
        result = parse_natural_language_prompt(prompt)
        
        assert result is not None
        assert result["tool_name"] == "create_environment"
        assert result["parameters"]["env_name"] == "myenv"
        assert result["parameters"]["python_version"] == "3.8"
        assert "numpy" in result["parameters"]["packages"]
    
    def test_create_environment_named(self):
        """Test environment creation with specific name."""
        prompt = "create a conda environment named myproject with pandas"
        result = parse_natural_language_prompt(prompt)
        
        assert result is not None
        assert result["tool_name"] == "create_environment"
        assert result["parameters"]["env_name"] == "myproject"
        assert "pandas" in result["parameters"]["packages"]
    
    def test_list_environments(self):
        """Test listing environments prompts."""
        prompts = [
            "list all my conda environments",
            "show all conda environments",
            "what are my conda environments"
        ]
        
        for prompt in prompts:
            result = parse_natural_language_prompt(prompt)
            assert result is not None
            assert result["tool_name"] == "list_environment"
            assert result["parameters"] == {}
    
    def test_show_environment_details(self):
        """Test showing environment details prompts."""
        prompt = "show details for environment myenv"
        result = parse_natural_language_prompt(prompt)
        
        assert result is not None
        assert result["tool_name"] == "show_environment_details"
        assert result["parameters"]["env_name"] == "myenv"
    
    def test_update_environment(self):
        """Test updating environment prompts."""
        prompt = "add pandas to myenv"
        result = parse_natural_language_prompt(prompt)
        
        assert result is not None
        assert result["tool_name"] == "update_environment"
        assert result["parameters"]["env_name"] == "myenv"
        assert "pandas" in result["parameters"]["packages"]
    
    def test_remove_environment(self):
        """Test removing environment prompts."""
        prompt = "remove environment oldenv"
        result = parse_natural_language_prompt(prompt)
        
        assert result is not None
        assert result["tool_name"] == "remove_environment"
        assert result["parameters"]["name"] == "oldenv"
    
    def test_search_packages(self):
        """Test searching packages prompts."""
        prompt = "search for scikit-learn"
        result = parse_natural_language_prompt(prompt)
        
        assert result is not None
        assert result["tool_name"] == "search_packages"
        assert result["parameters"]["package_name"] == "scikit-learn"
    
    def test_unsupported_prompt(self):
        """Test that unsupported prompts return None."""
        prompt = "do something completely unrelated"
        result = parse_natural_language_prompt(prompt)
        
        assert result is None
    
    def test_case_insensitive(self):
        """Test that prompts are case insensitive."""
        prompt = "CREATE A CONDA ENVIRONMENT WITH PYTHON 3.9"
        result = parse_natural_language_prompt(prompt)
        
        assert result is not None
        assert result["tool_name"] == "create_environment"
    
    def test_multiple_packages(self):
        """Test parsing multiple packages."""
        prompt = "create environment with numpy, pandas, and matplotlib"
        result = parse_natural_language_prompt(prompt)
        
        assert result is not None
        assert result["tool_name"] == "create_environment"
        packages = result["parameters"]["packages"]
        assert "numpy" in packages
        assert "pandas" in packages
        assert "matplotlib" in packages 