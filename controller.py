from pipeline import Pipeline
from devgpt_pipeline.extract.extractdata import DataExtractor
from devgpt_pipeline.load.data_loader import DataLoader
from devgpt_pipeline.translator.translator import LanguageTranslatorComponent
from devgpt_pipeline.lang_detect.langdetect import LanguageDetectionComponent
from devgpt_pipeline.preprocessing.preprocessing import PreProcessorComponent
from devgpt_pipeline.filter.filter import KeywordFilterComponent

pipeline = Pipeline()
extract_component = DataExtractor()
Load_component = DataLoader()
lang_detect_component = LanguageDetectionComponent()
translator_component = LanguageTranslatorComponent()
preprocessor_component = PreProcessorComponent(output_folder="tokenised_data")
filter_component = KeywordFilterComponent()
print("Pipeline created")
pipeline.add_component(extract_component)
pipeline.add_component(Load_component)
pipeline.add_component(lang_detect_component)
pipeline.add_component(translator_component)
pipeline.add_component(preprocessor_component)
pipeline.add_component(filter_component)

pipeline.run()
